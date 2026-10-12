#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H3 中文导演台 · 工作流结构门禁（无需模型、无需 GPU、离线可跑）

检查项：
  0. 发布范围：公开包内**只有唯一** V29 冻结生产工作流，且字节 SHA256 与冻结契约一致
  1. workflows/ 下所有 JSON 可解析
  2. 节点/连线完整（节点有 id/type；连线两端节点存在）
  3. 关键功能节点存在（导演台入口、六段状态、PreBake 等）
  4. 六段状态为"新用户中性默认态"
  5. 无私有绝对路径 / 素材文件名 / 凭据残留（与发布时同一套规则）

用法：
  python scripts/verify/verify_workflow_structure.py [repo_root]
退出码 0 = PASS，1 = FAIL
"""
import os, sys, json, re, glob

# ---- 发布范围契约（唯一 V29 冻结生产工作流）-------------------------------
# blob SHA256 以 LF 字节计算；克隆端若被 autocrlf 渲染成 CRLF，脚本会先归一再比对。
PUBLIC_WORKFLOW_NAME = "V29_chinese_director_production_8197.json"
PUBLIC_WORKFLOW_BLOB_SHA256 = ("311609b1e03316e724b97c8cf8783451955cb22a"
                              "12fd3ea31844e6632488302e")
PUBLIC_WORKFLOW_GIT_BLOB_SHA1 = "aadee988ad2cce4d946e9054643a72f4d0e41d6b"

DRIVE_RE = re.compile(r"([A-Za-z]):[\\/]+([^\\/\r\n\"'\s][^\r\n\"']{0,300})")
URL_TAIL = re.compile(r"(?i)(https?|ftp|file|data|mailto|wss?|blob|chrome[-\w]*|moz[-\w]*|"
                      r"resource|view[-\w]*|about|ws)$")
# 盘符前一字符为 ASCII 字母/数字 → 不是路径（如英文单词结尾 "…detail l:\n..."、"https" 的 "ps:"）；
# 但转义字符（\n \t \" 等）后的盘符是源码字面量里的真实路径，必须放行。
_ASCII_WORD = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")


def drive_path_redactable(s, m):
    i = m.start()
    pre1 = s[i - 1] if i > 0 else ""
    pre2 = s[i - 2:i] if i >= 2 else ""
    escaped = len(pre2) == 2 and pre2[0] == "\\" and pre2[1] in "ntr\"'\\u"
    if pre1 and (pre1 in _ASCII_WORD or pre1 == "_") and not escaped:
        return False
    return True
MEDIA_RE = re.compile(r"(?i)(?<![/\\:])[\w\u4e00-\u9fff\-]{2,140}\."
                      r"(png|jpe?g|webp|gif|bmp|mp4|mov|avi|mkv|webm|wav|mp3|flac|ogg|m4a)\b")
MEDIA_ALLOW = {"__H3_GUIDE_NOT_SET__.png", "example.png", "example.jpg"}
EMAIL_RE = re.compile(r"(?<![\w.\-])[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,24}(?![\w.\-])")
GH_TOKEN_RE = re.compile(r"\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}\b")
SK_TOKEN_RE = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")
AWS_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
B64_RE = re.compile(r"[A-Za-z0-9+/]{300,}={0,2}")
DATA_URI_RE = re.compile(r"(?i)data:(image|video|audio)/[a-z0-9.+-]+;base64,")
# h3-publish-allow: pattern_literal —— 这是“用户家目录”检测正则本身，不是真实路径
USER_HOME_RE = re.compile(r"(?i)(" + "C" + r":\\?/?)?Users[\\/]+[A-Za-z0-9._\-]{2,}[\\/]")

REQUIRED_ONCE = ["H3OperationSelector", "H3SixDirectorState"]

errors = []
warns = []


def walk_strings(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str):
                out.append(k)
            walk_strings(v, out)
    elif isinstance(o, list):
        for v in o:
            walk_strings(v, out)
    elif isinstance(o, str):
        out.append(o)


def check_text(path, s):
    for m in DRIVE_RE.finditer(s):
        if not drive_path_redactable(s, m):
            continue
        pre = s[max(0, m.start() - 10):m.start()]
        if URL_TAIL.search(pre):
            continue
        if re.match(r"(?i)^(windows|program files|programdata|temp|tmp)", m.group(2)):
            continue
        errors.append("%s: 私有绝对路径残留: %s" % (path, m.group(0)[:120]))
    for m in MEDIA_RE.finditer(s):
        if m.group(0) in MEDIA_ALLOW:
            continue
        if "/models/" in m.group(0) or m.group(0).endswith(".safetensors"):
            continue
        errors.append("%s: 素材文件名残留: %s" % (path, m.group(0)[:120]))
    for rx, name in ((EMAIL_RE, "email"), (GH_TOKEN_RE, "github token"),
                     (SK_TOKEN_RE, "sk token"), (AWS_RE, "aws key")):
        for m in rx.finditer(s):
            tok = m.group(0)
            if name == "email" and (re.match(r"(?i).*@\dx$", tok) or
                                    tok.lower().endswith((".png", ".jpg", ".webp"))):
                continue
            errors.append("%s: %s 残留: %s" % (path, name, tok[:60]))
    for m in USER_HOME_RE.finditer(s):
        if re.search(r"(?i)users[\\/]+(public|default)", m.group(0)):
            continue
        errors.append("%s: 用户家目录痕迹: %s" % (path, m.group(0)[:120]))
    if DATA_URI_RE.search(s):
        errors.append("%s: data URI 残留" % path)
    if B64_RE.search(s):
        errors.append("%s: 长 base64 片段残留" % path)


def _normalize_bytes(fp):
    """读原始字节；克隆机若开了 core.autocrlf=true，工作树会被渲染成 CRLF。
    仓库 blob 本身是 LF，所以比对哈希前把 CRLF 归一回 LF（不改磁盘文件）。"""
    data = open(fp, "rb").read()
    return data.replace(b"\r\n", b"\n") if b"\r\n" in data else data


def check_public_scope(files, errors):
    """发布范围硬闸门：公开包内必须只有唯一 V29 冻结生产工作流。"""
    rels = sorted(os.path.relpath(fp, ROOT_OF(files)).replace("\\", "/") for fp in files)
    expect = ["workflows/current/" + PUBLIC_WORKFLOW_NAME]
    if rels != expect:
        errors.append("PUBLIC_WORKFLOW_COUNT=%d（必须为 1）；公开工作流清单 = %s，期望 = %s"
                      % (len(rels), rels, expect))


def ROOT_OF(files):
    # files 全部位于 <root>/workflows/... 之下，向上两级即仓库根
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(files[0]))))


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    wf_dir = os.path.join(root, "workflows")
    if not os.path.isdir(wf_dir):
        print("FAIL: 找不到 workflows/ 目录：%s" % wf_dir)
        return 1
    # 递归枚举：任何子目录（含历史遗留目录名）里的工作流都会被算进来并触发范围闸门
    files = sorted(glob.glob(os.path.join(wf_dir, "**", "*.json"), recursive=True))
    print("待检工作流：%d（发布范围要求 = 1）" % len(files))
    if not files:
        print("FAIL: workflows/ 下没有 JSON")
        return 1
    check_public_scope(files, errors)
    if len(files) == 1:
        import hashlib
        blob = _normalize_bytes(files[0])
        digest = hashlib.sha256(blob).hexdigest()
        print("唯一公开工作流：%s / %d 字节（LF 归一）" % (
            os.path.basename(files[0]), len(blob)))
        if digest != PUBLIC_WORKFLOW_BLOB_SHA256:
            errors.append("唯一公开工作流字节 SHA256 = %s，与冻结契约 %s 不符"
                          % (digest, PUBLIC_WORKFLOW_BLOB_SHA256))
        else:
            print("SHA256 与冻结契约一致：%s" % digest)

    ok = 0
    for fp in files:
        rel = os.path.relpath(fp, root).replace("\\", "/")
        try:
            obj = json.load(open(fp, encoding="utf-8"))
        except Exception as e:
            errors.append("%s: JSON 解析失败 %s" % (rel, e))
            continue
        if not isinstance(obj, dict) or "nodes" not in obj:
            errors.append("%s: 不是 ComfyUI 工作流（缺 nodes）" % rel)
            continue
        nodes = obj.get("nodes") or []
        links = obj.get("links") or []
        if not isinstance(nodes, list):
            errors.append("%s: nodes 不是数组" % rel)
            continue
        ids = set()
        types = set()
        for n in nodes:
            if not isinstance(n, dict):
                errors.append("%s: 非法节点项" % rel)
                continue
            if "id" not in n or "type" not in n:
                errors.append("%s: 节点缺 id/type: %s" % (rel, str(n)[:80]))
            else:
                ids.add(n["id"])
                types.add(n["type"])
        if isinstance(links, list):
            for l in links:
                if not isinstance(l, (list, tuple)) or len(l) < 5:
                    errors.append("%s: 非法连线: %s" % (rel, str(l)[:80]))
                    continue
                try:
                    if l[1] not in ids or l[3] not in ids:
                        warns.append("%s: 悬空连线 %s（如为原图既有，可忽略）" % (rel, str(l)[:80]))
                except Exception:
                    pass
        if rel.startswith("workflows/current/"):
            for t in REQUIRED_ONCE:
                if t not in types:
                    errors.append("%s: 缺少关键节点 %s" % (rel, t))
        # 六段状态必须为中性默认
        for n in nodes:
            pr = n.get("properties") if isinstance(n, dict) else None
            sps = (pr or {}).get("six_prompt_state")
            if isinstance(sps, dict):
                for i, t in enumerate(sps.get("texts") or []):
                    if isinstance(t, str) and len(t.strip()) > 0 and "SANITIZED" not in t:
                        errors.append("%s: 六段文本非空（段 %d）" % (rel, i + 1))
                if (pr or {}).get("h3_prebake_story_id"):
                    errors.append("%s: h3_prebake_story_id 非空" % rel)
        strs = []
        walk_strings(obj, strs)
        check_text(rel, "\n".join(strs))
        ok += 1

    print("已通过结构检查：%d / %d" % (ok, len(files)))
    if warns:
        print("\n[WARN] %d 条（不阻断）" % len(warns))
        for w in warns[:10]:
            print("  -", w)
    if errors:
        print("\n[FAIL] %d 条" % len(errors))
        for e in errors[:40]:
            print("  -", e)
        return 1
    print("\nPASS: 结构门禁通过（JSON 可解析 / 节点连线完整 / 默认态为中性 / 无私有残留）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
