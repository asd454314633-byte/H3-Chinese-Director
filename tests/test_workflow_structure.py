#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H3 中文导演台 · 结构性回归测试（无需模型、无需 GPU、离线）

公开范围（v29.3 收口）：本仓库只发布**唯一**一套工作流
`workflows/current/V29_chinese_director_production_8197.json`（8197 冻结生产版）。
历史工作流、8207 实验工作流与合成工作流夹具已全部退出公开包，因此本测试的作用域
就是这一份文件；它的结构与冻结契约逐项对拍。

直接运行：
    python tests/test_workflow_structure.py
或用 pytest：
    pytest tests/
"""
import os, sys, json, glob, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "verify"))
import verify_workflow_structure as V  # noqa: E402

FAILED = []
PASSED = []

WF = os.path.join(ROOT, "workflows", "current", V.PUBLIC_WORKFLOW_NAME)

# 冻结结构契约（来自生产原件逐节点取证，见 docs/SECURITY_AND_PRIVACY.md 第 6 节）
FROZEN_NODES = 181
FROZEN_LINKS = 218
FROZEN_GROUPS = 22
FROZEN_SUBGRAPHS = 2          # definitions.subgraphs：连续-封装(8) + SDPose Multi-Person(7)
FROZEN_SUBGRAPH_NODES = 15
FROZEN_TOPLEVEL_TYPES = 76
REQUIRED_NODE_TYPES = ("H3OperationSelector", "H3SixDirectorState",
                       "MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo",
                       "LTXVSeparateAVLatent", "LTXVConcatAVLatent",
                       "SamplerCustomAdvanced", "VAEDecode", "VAEDecodeAudio",
                       "SaveVideo")
# 中文导演台的十路选择器矩阵（全部为本地作者自研语义层）
SELECTOR_TYPES = ("H3GenerationModeSelector", "H3ImageModeSelector",
                  "H3Ref2vaBackendSelector", "H3Ref2vaAttentionSelector",
                  "H3SpeedModeSelector", "H3Fl2vRouteSelector", "H3SizeModeSelector",
                  "H3OperationSelector", "H3GuideModeSelector",
                  "H3MemoryOptimizationSelector")
# 连续接续子图内的自研节点族
CONTINUATION_SUBGRAPH_TYPES = ("H3ContinuationPrepare", "H3ContinuationAssemble",
                               "H3ContinuationProvider", "H3ContinuationSave",
                               "H3ContinuationTrimOnce", "H3ContinuationGuides",
                               "H3ContinuationAudioBranch")


def check(name, fn):
    try:
        fn()
        PASSED.append(name)
    except AssertionError as e:
        FAILED.append((name, str(e)))
    except Exception as e:
        FAILED.append((name, "%s: %s" % (type(e).__name__, e)))


def load_wf():
    return json.load(open(WF, encoding="utf-8"))


def all_workflow_files():
    """递归枚举 workflows/ 下的 JSON —— 任何子目录里的第二套工作流都会被范围断言抓住。"""
    return sorted(glob.glob(os.path.join(ROOT, "workflows", "**", "*.json"), recursive=True))


def walk_strings(o, out):
    if isinstance(o, str):
        out.append(o)
    elif isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str):
                out.append(k)
            walk_strings(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o:
            walk_strings(v, out)


# ---------------------------------------------------------------- 范围与指纹

def test_only_one_public_workflow():
    files = all_workflow_files()
    rel = [os.path.relpath(f, ROOT).replace("\\", "/") for f in files]
    assert len(files) == 1, "PUBLIC_WORKFLOW_COUNT=%d（必须为 1）：%s" % (len(files), rel)
    assert rel == ["workflows/current/" + V.PUBLIC_WORKFLOW_NAME], rel


def test_public_workflow_blob_sha_matches_frozen_contract():
    raw = open(WF, "rb").read()
    norm = raw.replace(b"\r\n", b"\n") if b"\r\n" in raw else raw
    assert hashlib.sha256(norm).hexdigest() == V.PUBLIC_WORKFLOW_BLOB_SHA256, \
        "唯一公开工作流字节被改动（SHA256 与冻结契约不符）"


def test_no_history_directory_anywhere():
    for cand in ("history", os.path.join("workflows", "history")):
        p = os.path.join(ROOT, cand.replace("/", os.sep))
        assert not os.path.exists(p), "%s/ 仍存在（历史档案必须退出公开包）" % cand


def test_synthetic_workflow_fixture_is_not_public():
    p = os.path.join(ROOT, "fixtures", "synthetic", "synthetic_min_director_workflow.json")
    assert not os.path.exists(p), "合成夹具是可导入工作流，必须移出公开包"


# ---------------------------------------------------------------- 结构契约

def test_workflow_parses_and_is_comfyui_ui_format():
    obj = load_wf()
    for k in ("nodes", "links", "groups", "definitions", "extra", "version"):
        assert k in obj, "缺少顶层键 %s（不是完整的 ComfyUI UI 格式工作流）" % k
    assert isinstance(obj["nodes"], list) and isinstance(obj["links"], list)


def test_frozen_structure_counts():
    obj = load_wf()
    nodes = obj["nodes"]
    assert len(nodes) == FROZEN_NODES, "节点数 %d != 冻结契约 %d" % (len(nodes), FROZEN_NODES)
    assert len(obj["links"]) == FROZEN_LINKS, "连线数 %d != %d" % (len(obj["links"]), FROZEN_LINKS)
    assert len(obj["groups"]) == FROZEN_GROUPS, "分组数 %d != %d" % (len(obj["groups"]), FROZEN_GROUPS)
    subs = (obj.get("definitions") or {}).get("subgraphs") or []
    assert len(subs) == FROZEN_SUBGRAPHS, "子图数 %d != %d" % (len(subs), FROZEN_SUBGRAPHS)
    inner = sum(len(s.get("nodes") or []) for s in subs)
    assert inner == FROZEN_SUBGRAPH_NODES, "子图内节点数 %d != %d" % (inner, FROZEN_SUBGRAPH_NODES)
    types = set(n.get("type") for n in nodes if isinstance(n, dict))
    assert len(types) == FROZEN_TOPLEVEL_TYPES, \
        "顶层节点类型数 %d != %d" % (len(types), FROZEN_TOPLEVEL_TYPES)


def test_key_nodes_present():
    obj = load_wf()
    types = set(n.get("type") for n in obj["nodes"] if isinstance(n, dict))
    missing = [t for t in REQUIRED_NODE_TYPES if t not in types]
    assert not missing, "缺少关键功能节点: %s" % missing
    missing_sel = [t for t in SELECTOR_TYPES if t not in types]
    assert not missing_sel, "缺少中文导演台选择器矩阵节点: %s" % missing_sel
    sub_types = set()
    for sg in (obj.get("definitions") or {}).get("subgraphs") or []:
        for n in (sg.get("nodes") or []):
            if isinstance(n, dict):
                sub_types.add(n.get("type"))
    missing_cont = [t for t in CONTINUATION_SUBGRAPH_TYPES if t not in sub_types]
    assert not missing_cont, "连续接续子图缺少自研节点: %s" % missing_cont


def test_links_reference_existing_nodes():
    obj = load_wf()
    ids = set(n.get("id") for n in obj["nodes"] if isinstance(n, dict))
    dangling = [l for l in obj["links"]
                if isinstance(l, (list, tuple)) and len(l) >= 5 and (l[1] not in ids or l[3] not in ids)]
    assert not dangling, "存在悬空连线: %s" % dangling[:3]


def test_subgraph_nodes_reference_own_ids():
    obj = load_wf()
    bad = []
    for sg in (obj.get("definitions") or {}).get("subgraphs") or []:
        sids = set(n.get("id") for n in (sg.get("nodes") or []) if isinstance(n, dict))
        for l in (sg.get("links") or []):
            if isinstance(l, (list, tuple)) and len(l) >= 5 and (l[1] not in sids or l[3] not in sids):
                bad.append((sg.get("id"), str(l)[:60]))
    assert not bad, "子图内悬空连线: %s" % bad[:3]


# ---------------------------------------------------------------- 隐私契约

def test_six_segment_state_is_neutral_default():
    obj = load_wf()
    offenders = []
    for n in obj["nodes"] + [x for sg in (obj.get("definitions") or {}).get("subgraphs") or []
                             for x in (sg.get("nodes") or [])]:
        if not isinstance(n, dict):
            continue
        pr = n.get("properties") or {}
        sps = pr.get("six_prompt_state")
        if isinstance(sps, dict):
            for i, t in enumerate(sps.get("texts") or []):
                if isinstance(t, str) and t.strip():
                    offenders.append(("node %s" % n.get("id"), "seg%d" % (i + 1)))
            for k in ("goal", "settings"):
                if isinstance(sps.get(k), str) and sps[k].strip():
                    offenders.append(("node %s" % n.get("id"), k))
        for k in ("h3_prebake_story_id", "h3_six_prompts", "h3_prebake_last_plan",
                  "h3_prebake_bake_receipts"):
            v = pr.get(k)
            if v not in (None, "", [], {}):
                offenders.append(("node %s" % n.get("id"), k))
        for t in (pr.get("h3_prebake_texts") or []):
            if isinstance(t, str) and t.strip():
                offenders.append(("node %s" % n.get("id"), "h3_prebake_texts"))
    assert not offenders, "六段/PreBake 状态未回到中性默认: %s" % offenders[:5]


def test_no_private_paths_credentials_or_media_in_workflow():
    obj = load_wf()
    strs = []
    walk_strings(obj, strs)
    blob = json.dumps(obj, ensure_ascii=False)
    bad = []
    for m in V.DRIVE_RE.finditer(blob):
        if not V.drive_path_redactable(blob, m):
            continue
        pre = blob[max(0, m.start() - 10):m.start()]
        if V.URL_TAIL.search(pre):
            continue
        bad.append(("abs_path", m.group(0)[:60]))
    for rx, name in ((V.EMAIL_RE, "email"), (V.GH_TOKEN_RE, "github_token"),
                     (V.SK_TOKEN_RE, "sk_token"), (V.AWS_RE, "aws_key"),
                     (V.B64_RE, "base64_blob"), (V.DATA_URI_RE, "data_uri")):
        for m in rx.finditer(blob):
            bad.append((name, m.group(0)[:60]))
    for m in V.MEDIA_RE.finditer("\n".join(strs)):
        if m.group(0) in V.MEDIA_ALLOW:
            continue
        bad.append(("media_ref", m.group(0)[:60]))
    assert not bad, "工作流残留私有内容: %s" % bad[:6]


def test_no_embedded_private_image():
    """节点内不得有图片二进制 / data URI / 长 base64（EMBEDDED_PRIVATE_IMAGE = 0）。"""
    obj = load_wf()
    strs = []
    walk_strings(obj, strs)
    imgs = [s for s in strs if s.startswith("data:image") or s.startswith("data:video")
            or s.startswith("data:audio")]
    long_b64 = [s for s in strs if len(s) >= 300 and V.B64_RE.search(s)]
    assert not imgs, "存在内嵌 data URI 媒体: %d 处" % len(imgs)
    assert not long_b64, "存在长 base64 内嵌块: %d 处" % len(long_b64)


def test_synthetic_field_schema_fixtures_are_neutral():
    fp = os.path.join(ROOT, "fixtures", "synthetic", "synthetic_six_segment_state.json")
    assert os.path.isfile(fp), "缺少合成字段模式夹具"
    obj = json.load(open(fp, encoding="utf-8"))
    sps = obj["six_prompt_state"]
    assert sps["texts"] == [""] * 6, "夹具六段文本必须为空占位"
    assert sps["goal"] == "" and sps["settings"] == ""
    assert obj["h3_prebake_texts"] == [""] * 6
    assert obj["h3_prebake_story_id"] == ""
    assert obj["h3_prebake_revisions"] == [0] * 6


def main():
    print("H3 中文导演台 · 结构性回归测试（唯一 V29 冻结生产工作流）")
    print("=" * 60)
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            check(name, fn)
    for p in PASSED:
        print("  PASS  %s" % p)
    if FAILED:
        print("-" * 60)
        for n, e in FAILED:
            print("  FAIL  %s\n        %s" % (n, e))
        print("\n结果：%d 通过 / %d 失败" % (len(PASSED), len(FAILED)))
        return 1
    print("\n结果：%d 通过 / 0 失败 —— STRUCTURAL_REGRESSION=PASS" % len(PASSED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
