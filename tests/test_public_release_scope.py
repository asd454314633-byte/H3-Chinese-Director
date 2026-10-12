#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H3 中文导演台 · 公开发布范围契约测试（无需模型、无需 GPU、离线）

本测试把任务的收口要求固化为可执行断言（直接运行或 pytest 均可）：

    PUBLIC_WORKFLOW_COUNT = 1
    PUBLIC_WORKFLOW       = V29_chinese_director_production_8197.json
    HISTORY_DIRECTORY     = ABSENT
    PERSONAL_PROMPT_RESIDUE = 0
    EMBEDDED_PRIVATE_IMAGE  = 0

判定尺不新造：提示词残留复用 tests/test_no_personal_prompt_residue.py 的同一套
签名表与形状规则（含其 DOC_FILES 文件级白名单，判据未放宽）；内嵌图片复用
scripts/verify/verify_workflow_structure.py 的同一套正则。

直接运行：
    python tests/test_public_release_scope.py
"""
import glob
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "verify"))

import verify_workflow_structure as V  # noqa: E402

PUBLIC_WORKFLOW_COUNT = 1
PUBLIC_WORKFLOW = "workflows/current/" + V.PUBLIC_WORKFLOW_NAME
HISTORY_DIRECTORY = "ABSENT"
PERSONAL_PROMPT_RESIDUE = 0
EMBEDDED_PRIVATE_IMAGE = 0


def _load_sibling(name):
    path = os.path.join(HERE, name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FAILED = []
PASSED = []


def check(name, fn):
    try:
        fn()
        PASSED.append(name)
    except AssertionError as e:
        FAILED.append((name, str(e)))
    except Exception as e:  # noqa: BLE001 - 记账为失败，不静默跳过
        FAILED.append((name, "%s: %s" % (type(e).__name__, e)))


def workflow_json_files():
    """递归枚举 workflows/ 下的 JSON —— 任何子目录里的第二套工作流都会被抓住。"""
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


# ---------------------------------------------------------------- 范围断言

def test_public_workflow_count_is_one():
    files = workflow_json_files()
    rel = [os.path.relpath(f, ROOT).replace("\\", "/") for f in files]
    assert len(files) == PUBLIC_WORKFLOW_COUNT, \
        "PUBLIC_WORKFLOW_COUNT=%d（必须为 1）：%s" % (len(files), rel)


def test_public_workflow_is_the_frozen_v29():
    files = workflow_json_files()
    rel = [os.path.relpath(f, ROOT).replace("\\", "/") for f in files]
    assert rel == [PUBLIC_WORKFLOW], "PUBLIC_WORKFLOW=%s，期望 = [%s]" % (rel, PUBLIC_WORKFLOW)


def test_history_directory_is_absent():
    for cand in ("history", os.path.join("workflows", "history"),
                 os.path.join("manifests", "public_files.csv"),
                 os.path.join("manifests", "exclusions.csv"),
                 os.path.join("manifests", "exclusions_summary.csv")):
        p = os.path.join(ROOT, cand.replace("/", os.sep))
        assert not os.path.exists(p), "%s 仍存在（HISTORY_DIRECTORY 必须为 ABSENT）" % cand


def test_8207_experimental_line_is_absent():
    """8207 实验线源码整体退出公开包（用户裁决：删除镜像副本，不改判据）。"""
    p = os.path.join(ROOT, "custom_nodes", "local_author", "8207_line")
    assert not os.path.exists(p), "custom_nodes/local_author/8207_line/ 仍存在于公开树"


# ---------------------------------------------------------------- 隐私断言

def test_personal_prompt_residue_is_zero():
    """复用残留回归测试的同一把尺（签名表 + 形状规则 + 文件级白名单），判据未放宽。"""
    residue = _load_sibling("test_no_personal_prompt_residue")
    violations, sig_hits, unparsed = [], [], []
    residue._scan(violations, sig_hits, unparsed, root=ROOT)
    assert not unparsed, "内容无法解析导致扫描被跳过（尺坏即非 PASS）: %s" % unparsed[:5]
    assert not sig_hits, "已知个人创作提示词签名复现: %s" % sig_hits[:5]
    assert not violations, "PERSONAL_PROMPT_RESIDUE=%d（必须为 0）:\n%s" % (
        len(violations), "\n".join("  %s | %s" % v for v in violations[:10]))


def test_embedded_private_image_is_zero():
    """复用结构门禁的同一套正则：无 data URI 媒体、无长 base64 内嵌块。"""
    wf = os.path.join(ROOT, "workflows", "current", V.PUBLIC_WORKFLOW_NAME)
    obj = json.load(open(wf, encoding="utf-8"))
    strs = []
    walk_strings(obj, strs)
    imgs = [s for s in strs if s.startswith(("data:image", "data:video", "data:audio"))]
    long_b64 = [s for s in strs if len(s) >= 300 and V.B64_RE.search(s)]
    assert not imgs, "EMBEDDED_PRIVATE_IMAGE=%d（存在内嵌 data URI 媒体）" % len(imgs)
    assert not long_b64, "EMBEDDED_PRIVATE_IMAGE=%d（存在长 base64 内嵌块）" % len(long_b64)


def test_frozen_blob_sha_unchanged():
    """唯一工作流字节必须与冻结契约一致（本测试及其它公开改动不得触碰它）。"""
    wf = os.path.join(ROOT, "workflows", "current", V.PUBLIC_WORKFLOW_NAME)
    raw = open(wf, "rb").read()
    import hashlib
    norm = raw.replace(b"\r\n", b"\n") if b"\r\n" in raw else raw
    assert hashlib.sha256(norm).hexdigest() == V.PUBLIC_WORKFLOW_BLOB_SHA256, \
        "唯一公开工作流字节被改动（SHA256 与冻结契约不符）"


def main():
    print("H3 中文导演台 · 公开发布范围契约测试")
    print("=" * 60)
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            check(name, fn)
    for p in PASSED:
        print("  PASS  %s" % p)
    if FAILED:
        print("-" * 60)
        for n, e in FAILED:
            print("  FAIL  %s\n        %s" % (n, str(e)[:600]))
        print("\n结果：%d 通过 / %d 失败" % (len(PASSED), len(FAILED)))
        return 1
    print("\n结果：%d 通过 / 0 失败" % len(PASSED))
    print("PUBLIC_WORKFLOW_COUNT = %d" % PUBLIC_WORKFLOW_COUNT)
    print("PUBLIC_WORKFLOW = %s" % PUBLIC_WORKFLOW)
    print("HISTORY_DIRECTORY = %s" % HISTORY_DIRECTORY)
    print("PERSONAL_PROMPT_RESIDUE = %d" % PERSONAL_PROMPT_RESIDUE)
    print("EMBEDDED_PRIVATE_IMAGE = %d" % EMBEDDED_PRIVATE_IMAGE)
    print("PUBLIC_RELEASE_SCOPE = PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
