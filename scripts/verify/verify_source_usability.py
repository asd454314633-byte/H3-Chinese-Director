#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""公开包「源码可用性」门禁（离线、无模型、无 GPU、只读）。

为什么需要它：早期脱敏把「整行」替换成裸 <REDACTED_*> 占位符，占位符落到了
Python 语法位置上（参数默认值、dict 键行、raise 语句、注释块），于是 15 个
自研节点源码 **ast.parse 直接失败** —— 敏感信息是清了，源码却不可用了。
「没有扫出问题」不等于「留下的东西还能用」，所以本门禁逐项检查可解析性：

  PY        全部 .py：ast.parse + compile()
  JSON      全部 .json：json.load
  JS        全部 .js/.cjs/.mjs：node --check（node 不在则记 SKIPPED，不记 PASS）
  PS1       全部 .ps1：PowerShell 官方 Parser::ParseFile 错误计数
  TOKEN     裸脱敏占位符不得出现在**语法位置**（分档裁决，见下）
  PKG       每个自研节点包目录必须含 __init__.py / nodes.py / main.py（ComfyUI 可装载）

TOKEN 为什么要分档：脱敏把创作提示词正文整行换成占位符后，这些行必然落在
Python 字符串/docstring、JS 模板串、Markdown 散文里 —— 那是有意为之的公开披露
（见 docs/SECURITY_AND_PRIVACY.md），文件照样能解析，只是少了一句私货。
真正的缺陷只有一种：占位符落在语法位置上，把参数/键行/语句整行抹掉。
  .py                tokenize 精确定位；未被 STRING/COMMENT/FSTRING 覆盖 = FAIL
  .js/.cjs/.mjs/.json 由 node --check / json.load 裁决（语法位置的裸占位符一定让解析
                     通道判红），本类只要求该文件已 PASS 并记普查数
  .ps1               PowerShell ParseToken 按 CLR 类型定位（String/Comment 之外 = FAIL）
  散文与配置类        普查计数，不判死
任一"定位器"自身失败（读取失败/解析器无回执/零命中）一律判 FAIL —— 尺坏即非 PASS。

用法：python scripts/verify/verify_source_usability.py [仓库根目录]
"""
import ast
import collections
import io
import json
import os
import re
import shutil
import subprocess
import sys

BARE_TOKEN = re.compile(r"^<REDACTED_[A-Z_]*>\s*$")
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".pytest_cache"}
TXT_EXT = {".py", ".js", ".cjs", ".mjs", ".json", ".md", ".txt", ".csv", ".tsv",
           ".yaml", ".yml", ".ini", ".cfg", ".ps1", ".bat", ".cmd", ".sh",
           ".html", ".css"}
PARSE_COVERED = {".js", ".cjs", ".mjs", ".json"}
PROSE = {".md", ".txt", ".csv", ".tsv", ".yaml", ".yml", ".ini", ".cfg",
         ".bat", ".cmd", ".sh", ".html", ".css"}
ENTRY_FILES = {"__init__.py", "nodes.py", "main.py"}
CLASSES = ("PY", "JSON", "JS", "PS1", "TOKEN", "PKG")

# 一次 ParseFile 同时拿：语法错误数（ERRCOUNT）与字符串/注释 token 的行跨度（TK）。
# 按 Token 的 CLR 类型判定（StringToken 是字面量/可展开串的公共基类，CommentToken 是
# 注释），不猜 TokenKind 枚举名，避免引擎版本/本地化差异造成假判决。
PS_PARSE_CMD = (
    "$t=$null;$e=$null;"
    "[System.Management.Automation.Language.Parser]::ParseFile('__PATH__',[ref]$t,[ref]$e)|Out-Null;"
    "$r=@();"
    "foreach($x in $t){"
    "if($x -is [System.Management.Automation.Language.StringToken] -or "
    "$x -is [System.Management.Automation.Language.CommentToken]){"
    "$r+=($x.Extent.StartLineNumber.ToString()+'-'+$x.Extent.EndLineNumber.ToString())}};"
    "Write-Output ('TKCOUNT=' + $r.Count); "
    "Write-Output ('TK=' + ($r -join ',')); "
    "Write-Output ('ERRCOUNT=' + $e.Count)")


def ps_command(path):
    """路径用 __PATH__ 占位后替换（PowerShell 脚本体里满是 {}，不能用 str.format）。"""
    return PS_PARSE_CMD.replace("__PATH__", path.replace("'", "''"))


def rel(root, p):
    return os.path.relpath(p, root).replace("\\", "/")


def walk_ext(root, exts):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if os.path.splitext(f)[1].lower() in exts:
                out.append(os.path.join(dp, f))
    return sorted(out)


def read_text(p):
    return io.open(p, encoding="utf-8-sig", errors="replace").read()


def powershell():
    for cand in ("powershell", "pwsh"):
        got = shutil.which(cand)
        if got:
            return got
    return None


def py_covered_lines(text):
    """被字符串字面量/注释覆盖的行号集合；tokenize 失败返回 None（尺坏即非 PASS）。"""
    import tokenize
    cover = set()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except Exception:
        return None
    strlike = {tokenize.STRING, tokenize.COMMENT}
    for name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
        t = getattr(tokenize, name, None)
        if t is not None:
            strlike.add(t)
    for t in toks:
        if t.type in strlike:
            for row in range(t.start[0], t.end[0] + 1):
                cover.add(row)
    return cover


def ps_run(ps, path):
    """返回 (errcount:int|None, tk spans set, tccount:int|None, stderr)。"""
    r = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command",
                        ps_command(path)],
                       capture_output=True, text=True)
    out = r.stdout or ""
    m_err = re.search(r"ERRCOUNT=(\d+)", out)
    m_cnt = re.search(r"TKCOUNT=(\d+)", out)
    m_tk = re.search(r"TK=(.*)", out)
    covered = set()
    if m_tk:
        for span in m_tk.group(1).strip().split(","):
            mm = re.match(r"^(\d+)-(\d+)$", span.strip())
            if mm:
                for row in range(int(mm.group(1)), int(mm.group(2)) + 1):
                    covered.add(row)
    return (int(m_err.group(1)) if m_err else None,
            covered,
            int(m_cnt.group(1)) if m_cnt else None,
            (r.stderr or "").replace("\n", " "))


def check_py(root, fails):
    files = walk_ext(root, {".py"})
    bad = 0
    for p in files:
        try:
            src = read_text(p)
        except Exception as e:
            fails.append("PY 读取失败 %s: %s" % (rel(root, p), e))
            bad += 1
            continue
        try:
            ast.parse(src, filename=rel(root, p))
            compile(src, rel(root, p), "exec")
        except Exception as e:
            fails.append("PY 不可编译 %s: %s: %s" % (
                rel(root, p), type(e).__name__, str(e).replace("\n", " ")[:120]))
            bad += 1
    return len(files), bad


def check_json(root, fails):
    files = walk_ext(root, {".json"})
    bad, failed = 0, set()
    for p in files:
        try:
            json.load(io.open(p, encoding="utf-8-sig"))
        except Exception as e:
            fails.append("JSON 解析失败 %s: %s" % (rel(root, p), str(e)[:120]))
            failed.add(rel(root, p))
            bad += 1
    return len(files), bad, failed


def check_js(root, fails, notes):
    node = shutil.which("node")
    files = walk_ext(root, {".js", ".cjs", ".mjs"})
    bad, failed = 0, set()
    if not node:
        notes.append("JS=SKIPPED_NO_NODE（未记 PASS）")
        return len(files), None, failed
    for p in files:
        r = subprocess.run([node, "--check", p], capture_output=True, text=True)
        if r.returncode != 0:
            fails.append("JS 语法错误 %s: %s" % (
                rel(root, p), (r.stderr or "").strip().replace("\n", " ")[:170]))
            failed.add(rel(root, p))
            bad += 1
    return len(files), bad, failed


def check_ps1(root, fails, notes, ps):
    files = walk_ext(root, {".ps1"})
    if not ps:
        notes.append("PS1=SKIPPED_NO_POWERSHELL（未记 PASS）")
        return len(files), None
    bad = 0
    for p in files:
        err, _cov, _tc, stderr = ps_run(ps, p)
        if err is None:
            fails.append("PS1 无法判定 %s: 解析器无回执（尺坏即非 PASS）err=%s" % (
                rel(root, p), stderr[:100]))
            bad += 1
        elif err != 0:
            fails.append("PS1 语法错误 %s: ERCOUNT=%d" % (rel(root, p), err))
            bad += 1
    return len(files), bad


def check_tokens(root, fails, notes, covered_failed, ps):
    """裸占位符位置裁决（见模块 docstring）。返回 (文件数, 违规数, 普查, 散文清单)。"""
    n_files = bad = 0
    census = collections.Counter()
    prose, ps_pending = [], []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            ext = os.path.splitext(f)[1].lower()
            if ext not in TXT_EXT:
                continue
            p = os.path.join(dp, f)
            r_rel = rel(root, p)
            n_files += 1
            try:
                text = read_text(p)
            except Exception as e:
                fails.append("TOKEN 读取失败 %s: %s" % (r_rel, e))
                bad += 1
                continue
            bare = [i for i, l in enumerate(text.split("\n"), 1) if BARE_TOKEN.match(l)]
            if not bare:
                continue
            census[ext] += len(bare)
            if ext == ".py":
                cover = py_covered_lines(text)
                if cover is None:
                    fails.append("TOKEN 无法定位 %s: tokenize 失败（尺坏即非 PASS）" % r_rel)
                    bad += 1
                    continue
                hit = [i for i in bare if i not in cover]
                if hit:
                    fails.append("TOKEN 占位符落在语法位置 %s:%s —— 脱敏破坏了代码结构" % (
                        r_rel, ",".join(map(str, hit[:6]))))
                    bad += 1
            elif ext == ".ps1":
                ps_pending.append((r_rel, bare))
            elif ext in PARSE_COVERED:
                if r_rel in covered_failed:
                    fails.append("TOKEN %s 含裸占位符且其解析通道已判红 —— 需按语法位置修复" % r_rel)
                    bad += 1
                else:
                    census["(parse-covered-ok)"] += len(bare)
            elif ext in PROSE:
                prose.append((r_rel, len(bare)))
            else:
                fails.append("TOKEN %s 扩展名 %s 未归类，无法判定占位符位置" % (r_rel, ext))
                bad += 1

    for r_rel, bare in ps_pending:
        if not ps:
            notes.append("PS1 TOKEN=SKIPPED_NO_POWERSHELL（%s 未记 PASS）" % r_rel)
            continue
        err, covered, tccount, stderr = ps_run(ps, os.path.join(root, r_rel.replace("/", os.sep)))
        if err is None or tccount is None:
            fails.append("TOKEN 无法定位 %s: ParseToken 无回执（尺坏即非 PASS）err=%s" % (
                r_rel, stderr[:100]))
            bad += 1
            continue
        if tccount == 0:
            # 正控制缺失：含裸占位符的 .ps1 里连一个字符串/注释 token 都没定位到 = 尺坏
            fails.append("TOKEN 定位器零命中 %s: TKCOUNT=0（尺坏即非 PASS，不得据此判干净）" % r_rel)
            bad += 1
            continue
        hit = [i for i in bare if i not in covered]
        if hit:
            fails.append("TOKEN 占位符落在语法位置 %s:%s —— 脱敏破坏了代码结构" % (
                r_rel, ",".join(map(str, hit[:6]))))
            bad += 1
    return n_files, bad, census, prose


def check_pkg(root, fails):
    """每个自研节点包必须自带入口文件 —— 安装文档是整目录 xcopy，缺入口即装不上。"""
    pkgs = []
    la = os.path.join(root, "custom_nodes", "local_author")
    if os.path.isdir(la):
        for line in sorted(os.listdir(la)):
            ld = os.path.join(la, line)
            if not os.path.isdir(ld):
                continue
            for pkg in sorted(os.listdir(ld)):
                pd = os.path.join(ld, pkg)
                if os.path.isdir(pd) and any(f.endswith(".py") for f in os.listdir(pd)):
                    pkgs.append(pd)
    bad = 0
    for d in pkgs:
        if not (ENTRY_FILES & set(os.listdir(d))):
            fails.append("PKG 节点包缺少入口文件（ComfyUI 无法装载）: %s" % rel(root, d))
            bad += 1
    return len(pkgs), bad


def run(root):
    """跑全部六类，返回 counts/fails/notes/census/prose。供 CLI 与测试共用。"""
    root = os.path.abspath(root)
    fails, notes = [], []
    ps = powershell()
    counts = {}
    counts["PY"] = check_py(root, fails)
    n_json, b_json, json_failed = check_json(root, fails)
    counts["JSON"] = (n_json, b_json)
    n_js, b_js, js_failed = check_js(root, fails, notes)
    counts["JS"] = (n_js, b_js)
    counts["PS1"] = check_ps1(root, fails, notes, ps)
    n_tok, b_tok, census, prose = check_tokens(
        root, fails, notes, json_failed | js_failed, ps)
    counts["TOKEN"] = (n_tok, b_tok)
    counts["PKG"] = check_pkg(root, fails)
    return {"counts": counts, "fails": fails, "notes": notes,
            "census": census, "prose": prose}


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    res = run(root)
    counts, fails, notes = res["counts"], res["fails"], res["notes"]
    print("公开包源码可用性门禁 —— 根目录：%s" % root)
    print("=" * 68)
    for k in CLASSES:
        tot, b = counts[k]
        state = "SKIPPED" if b is None else ("OK" if b == 0 else "FAIL(%d)" % b)
        print("  %-6s 对象 %-4d -> %s" % (k, tot, state))
    inlit = sum(v for k, v in res["census"].items() if k != "(parse-covered-ok)")
    print("  裸占位符普查：%d 行（位于代码内字面量/docstring/散文中的有意披露，非缺陷）"
          % inlit)
    if res["prose"]:
        print("  散文/配置内占位行：%d 个文件（首个：%s）" % (
            len(res["prose"]), res["prose"][0][0]))
    for n in notes:
        print("  NOTE " + n)
    if fails:
        print("\n[FAIL] %d 条" % len(fails))
        for f in fails[:40]:
            print("  - " + f)
        print("\nSOURCE_USABILITY=FAIL")
        return 1
    skipped = [k for k, (_t, b) in counts.items() if b is None]
    print("\nSOURCE_USABILITY=PASS" + ("" if not skipped else
          "  (未覆盖项: %s —— 记为 SKIPPED 而非 PASS)" % ",".join(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
