#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pin and diff the SDPose sub-graph against its OFFICIAL blueprint.

Why this exists
---------------
The v29.3 audit compared the published sub-graph against the *local* ComfyUI
`blueprints/` copy and, having no upstream commit pinned, could only claim
`SEMANTIC_LEVEL_MATCH`. The upstream is a **separate MIT repository**:

    https://github.com/Comfy-Org/workflow_templates            (MIT)
    blueprints/video_to_pose_map_sdpose_multi_person.json
    commit cdccb2ee7a7cd0baee4630cf7186283a98ab408f (main, 2026-10-12T13:52:16Z)
    blob   6f6d7ab146a5b143f70bc98d444a7a64829a94ea  (33268 B)
    sha256 92e31fb99f4a005a9263c296429c99eb0847567d64b1f3a35fa42839e0cbfec2

ComfyUI's engine is GPL-3.0, but that licence does **not** travel to an
independently published MIT template repository. The audit's `THIRD_PARTY_NOTICES`
also claimed "本仓库不重新分发任何第三方项目源码" and "对第三方节点的源码未做修改",
both of which are false for this sub-graph: it is a published, modified copy of
the official blueprint.

This script re-derives the comparison from the pinned upstream file and prints
both the invariants (external contract identical) and the modifications (node /
link / parameter differences), so the NOTICE can state them precisely.

It never modifies the workflow JSON; it only reads it.

    python scripts/verify/verify_sdpose_blueprint.py
    python scripts/verify/verify_sdpose_blueprint.py --blueprint <path> [--json out.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW = ROOT / "workflows" / "current" / "V29_chinese_director_production_8197.json"

UPSTREAM = {
    "repo": "Comfy-Org/workflow_templates",
    "url": "https://github.com/Comfy-Org/workflow_templates",
    "license": "MIT",
    "commit": "cdccb2ee7a7cd0baee4630cf7186283a98ab408f",
    "commit_date": "2026-10-12T13:52:16Z",
    "path": "blueprints/video_to_pose_map_sdpose_multi_person.json",
    "blob_sha1": "6f6d7ab146a5b143f70bc98d444a7a64829a94ea",
    "size": 33268,
    "sha256": "92e31fb99f4a005a9263c296429c99eb0847567d64b1f3a35fa42839e0cbfec2",
    "raw": ("https://raw.githubusercontent.com/Comfy-Org/workflow_templates/"
            "main/blueprints/video_to_pose_map_sdpose_multi_person.json"),
}

DEFAULT_BLUEPRINT = ROOT / "docs" / "evidence" / "sdpose_blueprint_pinned.json"


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha(obj):
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()[:16]


def find_subgraph(obj):
    """Return (name, definition) of the published SDPose sub-graph."""
    defs = obj.get("definitions", {}).get("subgraphs", [])
    hits = [(d.get("name", ""), d) for d in defs
            if "sdpose" in str(d.get("name", "")).lower()]
    return hits[0] if hits else (None, None)


def blueprint_subgraph(bp):
    """The official file is a workflow wrapper: the blueprint lives in
    `definitions.subgraphs[0]` (top level has a single placeholder node)."""
    subs = bp.get("definitions", {}).get("subgraphs", [])
    if not subs:
        return None, None
    return subs[0].get("name"), subs[0]


def flatten(o, prefix=""):
    """Flatten dict/list into {path: scalar} for a field-level diff."""
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flatten(v, f"{prefix}[{i}]"))
        out[prefix + "[len]"] = len(o)
    else:
        out[prefix] = o
    return out


def diff_leaves(a, b):
    fa, fb = flatten(a), flatten(b)
    keys = set(fa) | set(fb)
    return sorted(k for k in keys if fa.get(k) != fb.get(k))


def node_summary(nodes):
    return [n.get("type") for n in nodes]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", default=str(DEFAULT_BLUEPRINT))
    ap.add_argument("--fetch", action="store_true",
                    help="从上游 raw 重新下载蓝图并覆盖本地钉住副本")
    ap.add_argument("--json", dest="json_out", help="把结果写成 JSON")
    a = ap.parse_args(argv)

    wf_raw = WORKFLOW.read_bytes()
    wf_sha256 = hashlib.sha256(wf_raw.replace(b"\r\n", b"\n")).hexdigest()
    obj = json.loads(wf_raw.decode("utf-8"))

    bp_path = Path(a.blueprint)
    if a.fetch or not bp_path.is_file():
        import urllib.request
        bp_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(UPSTREAM["raw"], timeout=60) as r:
            data = r.read()
        bp_path.write_bytes(data)
        print("fetched %s (%d B)" % (UPSTREAM["raw"], len(data)))
    bp_raw = bp_path.read_bytes()
    bp = json.loads(bp_raw.decode("utf-8"))

    checks = []
    ok = True

    def record(name, passed, detail):
        nonlocal ok
        checks.append({"check": name, "state": "PASS" if passed else "FAIL",
                       "detail": detail})
        if not passed:
            ok = False

    # 0) the pinned upstream file really is the pinned blob
    bp_blob = hashlib.sha1(b"blob %d\0" % len(bp_raw) + bp_raw).hexdigest()
    record("blueprint_blob_matches_pin", bp_blob == UPSTREAM["blob_sha1"],
           "got=%s expected=%s" % (bp_blob, UPSTREAM["blob_sha1"]))
    record("blueprint_sha256_matches_pin",
           hashlib.sha256(bp_raw).hexdigest() == UPSTREAM["sha256"],
           hashlib.sha256(bp_raw).hexdigest())

    # 1) the workflow is untouched
    record("workflow_blob_unchanged",
           wf_sha256 == "311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e",
           wf_sha256)
    record("workflow_shape_unchanged",
           (len(obj.get("nodes", [])), len(obj.get("links", [])),
            len(obj.get("definitions", {}).get("subgraphs", []))) == (181, 218, 2),
           "nodes=%d links=%d subgraphs=%d" % (len(obj.get("nodes", [])),
                                               len(obj.get("links", [])),
                                               len(obj.get("definitions", {}).get("subgraphs", []))))

    name, pub = find_subgraph(obj)
    bp_name, bp_sub = blueprint_subgraph(bp)
    record("sdpose_subgraph_present", pub is not None, str(name))
    record("blueprint_subgraph_present", bp_sub is not None, str(bp_name))
    if pub is None or bp_sub is None:
        print("SDPOSE_BLUEPRINT=FAIL"); return 1
    bp = bp_sub

    # 2) external contract identical -> it is really that blueprint
    for key in ("inputs", "outputs"):
        same = canon(pub.get(key)) == canon(bp.get(key))
        record("subgraph_%s_identical" % key, same,
               "pub=%d bp=%d sha(pub)=%s sha(bp)=%s"
               % (len(pub.get(key, [])), len(bp.get(key, [])),
                  sha(pub.get(key)), sha(bp.get(key))))

    # 3) node / link inventory
    pn, bn = pub.get("nodes", []), bp.get("nodes", [])
    pl, bl = pub.get("links", []), bp.get("links", [])
    record("node_type_set_identical",
           sorted(node_summary(pn)) == sorted(node_summary(bn)),
           "pub=%s" % sorted(node_summary(pn)))
    record("node_count_identical", len(pn) == len(bn), "%d vs %d" % (len(pn), len(bn)))
    record("link_count_identical", len(pl) == len(bl), "%d vs %d" % (len(pl), len(bl)))

    # 4) the modifications this project made (must be listed in the NOTICE)
    node_paths = diff_leaves(pn, bn)
    link_paths = diff_leaves(pl, bl)
    top = [p for p in (name, pub.get("category"), bp.get("category"))
           if p is not None]
    record("subgraph_id_rewritten", pub.get("id") != bp.get("id"),
           "pub=%s bp=%s" % (pub.get("id"), bp.get("id")))
    record("subgraph_name_renamed", pub.get("name") != bp.get("name"),
           "pub=%r bp=%r" % (pub.get("name"), bp.get("name")))

    result = {
        "upstream": UPSTREAM,
        "workflow_sha256": wf_sha256,
        "subgraph": {"name": pub.get("name"), "id": pub.get("id")},
        "blueprint": {"name": bp.get("name"), "id": bp.get("id"),
                      "category": bp.get("category")},
        "differing_node_leaf_paths": node_paths,
        "differing_link_leaf_paths": link_paths,
        "n_differing_node_leaves": len(node_paths),
        "n_differing_link_leaves": len(link_paths),
        "checks": checks,
        "state": "PASS" if ok else "FAIL",
    }

    print("SDPose 子图 vs 官方 blueprint（上游 %s @ %s）" % (UPSTREAM["repo"], UPSTREAM["commit"][:12]))
    print("=" * 68)
    for c in checks:
        print("  %-4s %s  %s" % (c["state"], c["check"], c["detail"]))
    print("-" * 68)
    print("  节点叶子字段差异 %d 处；连线叶子字段差异 %d 处" % (len(node_paths), len(link_paths)))
    for p in node_paths[:12]:
        print("      node %s" % p)
    if len(node_paths) > 12:
        print("      ... 其余 %d 处见 JSON 输出" % (len(node_paths) - 12))
    for p in link_paths[:8]:
        print("      link %s" % p)
    print("\nSDPOSE_BLUEPRINT=%s" % result["state"])

    if a.json_out:
        Path(a.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
