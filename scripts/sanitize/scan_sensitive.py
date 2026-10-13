#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H3 中文导演台 · 全树敏感项扫描（与发布时同一套规则）

用法：
  python scripts/sanitize/scan_sensitive.py [repo_root]
退出码 0 = PASS（零命中），1 = FAIL
"""
import os, sys, re, hashlib

# 盘符路径正则（与本仓库发布工程所用清洗规则一致，四条并用）：
#  DRIVE_RE / DRIVE_RE_ESC —— 大写盘符。反向预查排除 "https://" 的 "s://"、
#      "...models:\n  base_path: <大写盘符>:/..." 这类把 `s:` 当盘符后吞掉真路径的误判；
#      ESC 变体处理源码字面量里 "\n\n<大写盘符>:/..."（前一字符是字母 n，反向预查会漏掉）。
#      （说明文字中不写真实盘符，避免本脚本扫描自己时命中。）
#      注意：判定盘符前一个字符时不能用 str.isalnum()——它对中文返回 True，
#      中文 + 大写盘符紧跟的写法会被误判为非路径而漏网；本脚本改用反向预查天然规避。
#  LOWER_DRIVE_* + PRIVATE_ROOT_HINT —— 小写盘符兜底：真实 Windows 路径极少用小写盘符，
#      因此要求路径片段命中私有根词才判定为路径，避开 "character’s:\nface" 这类误报。
_DRIVE_TAIL = r"([A-Z]):[\\/]+([^\\/\r\n\"'\s][^\r\n\"']{0,300})"
_LOWER_TAIL = r"([a-z]):[\\/]+([^\\/\r\n\"'\s][^\r\n\"']{0,300})"
DRIVE_RE = re.compile(r"(?<![A-Za-z0-9])" + _DRIVE_TAIL)
DRIVE_RE_ESC = re.compile(r"(?<=[\\][ntr\"'\\u])" + _DRIVE_TAIL)
LOWER_DRIVE_RE = re.compile(r"(?<![A-Za-z0-9])" + _LOWER_TAIL)
LOWER_DRIVE_ESC_RE = re.compile(r"(?<=[\\][ntr\"'\\u])" + _LOWER_TAIL)
PRIVATE_ROOT_HINT_RE = re.compile(
    r"(?i)(comfyui|users[\\/]|models[\\/]|venv|workspace|director|h3[_\-]|"
    r"项目|导演台|零复刻|program files)")
DRIVE_RES = (DRIVE_RE, DRIVE_RE_ESC, LOWER_DRIVE_RE, LOWER_DRIVE_ESC_RE)
KEEP_PATH_RE = re.compile(
    r"(?i)^(windows|program files(?: \(x86\))?|programdata|temp|tmp|"
    r"users[\\/]+public|users[\\/]+default)(?:[\\/]|$)")
URL_TAIL = re.compile(r"(?i)(https?|ftp|file|data|mailto|wss?|blob|chrome[-\w]*|moz[-\w]*|"
                      r"resource|view[-\w]*|about|ws)$")
MEDIA_RE = re.compile(r"(?i)(?<![/\\:])[\w\u4e00-\u9fff\-]{2,140}\."
                      r"(png|jpe?g|webp|gif|bmp|mp4|mov|avi|mkv|webm|wav|mp3|flac|ogg|m4a)\b")
SHOWCASE_MEDIA_SHA256 = {
    'assets/showcase/h3-six-segment-demo-github.mp4': 'da7039a18f7c7afa15fcf96876d64fa874c6be6993c23829a7b245fdd42ae37b',
    'assets/showcase/showcase-cover.jpg': 'bc6e3dd8e1db888e562a1cb0827f6bb52e5b1dbd492c36b62a941fd9195601d9',
    'assets/showcase/six-segment-panel-redacted.png': '19ba3f40fa328d5848e02cf5d34264544c87b2a06052d7e61accf67f6d5c015c',
    'assets/showcase/demo-preview.gif': '6322bcfb9364d02e2ba9582a478994ed540abd6e8fd40a080d5a33b3b2a15c8a',
}
MEDIA_ALLOW = {"__H3_GUIDE_NOT_SET__.png", "example.png", "example.jpg"}
MEDIA_ALLOW.update(os.path.basename(p) for p in SHOWCASE_MEDIA_SHA256)
EMAIL_RE = re.compile(r"(?<![\w.\-])[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,24}(?![\w.\-])")
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
GH_TOKEN_RE = re.compile(r"\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}\b")
SK_TOKEN_RE = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")
AWS_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}\b")
LAN_IP_RE = re.compile(r"(?<!\d)(?:(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\."
                       r"\d{1,3}\.\d{1,3}\.\d{1,3})(?!\d)")
SECRET_KV_RE = re.compile(r"(?i)\b(api[_\-]?key|secret|password|passwd|token|authorization|cookie|"
                          r"access[_\-]?key|private[_\-]?key)\b\s*[:=]\s*"
                          r"([\"']([A-Za-z0-9._\-]{16,})[\"']|([A-Za-z0-9._\-]{24,}))")
B64_RE = re.compile(r"[A-Za-z0-9+/]{300,}={0,2}")
DATA_URI_RE = re.compile(r"(?i)data:(image|video|audio)/[a-z0-9.+-]+;base64,")
# h3-publish-allow: pattern_literal —— 这是“用户家目录”检测正则本身，不是真实路径
USER_HOME_RE = re.compile(r"(?i)(" + "C" + r":\\?/?)?Users[\\/]+[A-Za-z0-9._\-]{2,}[\\/]")
CN_CTX_RE = re.compile(r"[\u4e00-\u9fff]|phone|mobile|tel|手机|电话|联系")

TEXT_EXT = {".md", ".txt", ".csv", ".tsv", ".json", ".yaml", ".yml", ".toml", ".ini",
            ".cfg", ".log", ".html", ".htm", ".xml", ".py", ".js", ".mjs", ".cjs",
            ".ts", ".vue", ".css", ".ps1", ".cmd", ".bat", ".sh"}

hits = []


def scan(path, rel, text):
    def add(kind, sample):
        hits.append((rel, kind, sample[:160]))

    for rx in DRIVE_RES:
        for m in rx.finditer(text):
            pre = text[max(0, m.start() - 10):m.start()]
            if URL_TAIL.search(pre):
                continue
            if KEEP_PATH_RE.match(m.group(2)):
                continue
            # 已脱敏产物拼接（系统路径白名单前缀 + <REDACTED_*> 占位符）不含个人信息
            if "<REDACTED_" in m.group(0):
                continue
            if m.group(1).islower() and not PRIVATE_ROOT_HINT_RE.search(m.group(2)):
                continue
            add("abs_path", m.group(0))
    for m in MEDIA_RE.finditer(text):
        if m.group(0) in MEDIA_ALLOW:
            continue
        if "/models/" in m.group(0) or m.group(0).endswith(".safetensors"):
            continue
        # 泛化媒体名（clip/output/preview/example/frame 等示意名）不是个人素材文件名
        stem = m.group(0).rsplit(".", 1)[0].lower()
        if re.fullmatch(r"(?i)(clip|output|out|preview|example|sample|frame[ _-]?\d*|"
                        r"video[ _-]?\d*|image[ _-]?\d*|test[ _-]?\d*|input|temp|tmp"
                        r"|render[ _-]?\d*|result\d*)", stem):
            continue
        add("media_ref", m.group(0))
    for m in EMAIL_RE.finditer(text):
        tok = m.group(0)
        if re.match(r"(?i).*@\dx$", tok) or tok.lower().endswith((".png", ".jpg", ".webp")):
            continue
        add("email", tok)
    for m in PHONE_RE.finditer(text):
        ctx = text[max(0, m.start() - 14):m.end() + 14]
        if CN_CTX_RE.search(ctx):
            add("phone", m.group(0))
    for rx, name in ((GH_TOKEN_RE, "github_token"), (SK_TOKEN_RE, "sk_token"),
                     (AWS_RE, "aws_key"), (JWT_RE, "jwt")):
        for m in rx.finditer(text):
            add(name, m.group(0)[:40])
    for m in LAN_IP_RE.finditer(text):
        add("lan_ip", m.group(0))
    for m in SECRET_KV_RE.finditer(text):
        val = m.group(3) or m.group(4) or ""
        if re.match(r"^[a-z_][a-z0-9_.]*$", val):
            continue
        add("secret_kv", m.group(0)[:60])
    for m in USER_HOME_RE.finditer(text):
        if re.search(r"(?i)users[\\/]+(public|default)", m.group(0)):
            continue
        add("user_home", m.group(0))
    if DATA_URI_RE.search(text):
        add("data_uri", "data:...")
    if B64_RE.search(text):
        add("base64_blob", "...")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, root).replace("\\", "/")
            ext = os.path.splitext(fn)[1].lower()
            if ext == "":
                # 无扩展名（LICENSE/README 类）不算未知二进制
                continue
            if ext not in TEXT_EXT:
                if rel in SHOWCASE_MEDIA_SHA256:
                    with open(fp, "rb") as public_asset:
                        actual_sha = hashlib.sha256(public_asset.read()).hexdigest()
                    if actual_sha != SHOWCASE_MEDIA_SHA256[rel]:
                        hits.append((rel, "public_showcase_sha_mismatch", actual_sha))
                    continue
                hits.append((rel, "unknown_binary_ext", ext))
                continue
            try:
                text = open(fp, encoding="utf-8", errors="replace").read()
            except Exception as e:
                hits.append((rel, "unreadable", str(e)))
                continue
            n += 1
            if ext == ".json":
                try:
                    import json as _j
                    obj = _j.loads(text)
                    text = _j.dumps(obj, ensure_ascii=False)
                except Exception:
                    pass
            scan(fp, rel, text)
    print("已扫描文本文件：%d" % n)
    if hits:
        print("FAIL: 命中 %d 项" % len(hits))
        for h in hits[:50]:
            print("  -", h[1], "|", h[0][:90], "|", h[2][:110])
        return 1
    print("PASS: 零命中（无私有路径 / 素材名 / 身份 / 凭据 / 内嵌二进制）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
