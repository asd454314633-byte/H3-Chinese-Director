# -*- coding: utf-8 -*-
"""回归测试：公开包内不得存在个人创作提示词残留。

背景（v29.2 修复的漏报）：历史工作流中曾残留完整的个人创作提示词（具体人物、姿势、身份替换约束等），
当时的脱敏规则只覆盖中文对白格式 `<d>[Chinese]...`，英文长创作提示词不在检测范围。

v29.3 收口后，那 14 份历史工作流随 `workflows/history/`、`history/` 一起退出公开包；
**本测试不因此缩小作用域**：作用域从"全部工作流 JSON"扩大为"公开树内的全部文本文件"，
凭据/路径类由 `scripts/sanitize/scan_sensitive.py` 负责，本测试负责"创作提示词形状"。

双保险：
1. 已知 5 个个人创作提示词签名（MD5 前 8 位）必须永远不再出现（作用于全树字节）。
2. 规则扫描：长度 ≥500 字符、命中创作词汇 / 描述符堆叠 / 负向提示词特征、且**不含**通用模板
   占位符（`<Subject N>` / `<Picture N>` 等）的字符串，必须属于显式文档白名单，否则判 FAIL。

直接运行：python tests/test_no_personal_prompt_residue.py
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 已知个人创作提示词签名（v29.2 已替换为 <REDACTED_PERSONAL_PROMPT>）
PERSONAL_SIGNATURES = {
    "43bf68c6",  # Use Image 1 as the only character reference / AI girlfriend idle clip
    "41557be5",  # Scene: Hyperreal desert-storm aesthetic
    "73732c50",  # A photorealistic young woman in a beige top
    "4cc6efbf",  # REFERENCE RULES raised-leg pose (Qwen image edit)
    "8b655a83",  # extra woman ... negative prompt list (Qwen image edit)
}

KEYWORDS = re.compile(
    r"\b(woman|man|girl|boy|pose|posture|outfit|lingerie|nsfw|nude|body|figure|"
    r"lighting|camera|cinematic|photorealistic|composition|background|face|skin|"
    r"hair|expression|gesture|scene|costume|dressed|提示词|人物|姿势|动作|服装|"
    r"场景|镜头|构图|光线|高清|写实)\b",
    re.I,
)
DESCRIPTOR_RUN = re.compile(r"(\b[a-z]+ [a-z]+ [a-z]+ [a-z]+(?:,|\n)){5,}", re.I)
NEG_SIGNS = re.compile(
    r"\b(extra|duplicate|deformed|blurry|low quality|worst quality|multiple|cloned|unwanted)\b",
    re.I,
)
# 通用模板占位符：<Subject 1> / <Picture 1> / {{...}} / ${...} / <d>[...] 对白
PLACEHOLDER = re.compile(r"<(Subject|Picture|人物|图片)\s?\d+>|\{\{|\$\{|<d>\[")
MIN_LEN = 500

# 内容级白名单：命中前缀的长文本是节点功能文档 / 官方规范 / 自研模型指令模板，
# 不是个人创作内容（个人创作内容一律由下面的签名判定与形状判定共同把关）
DOC_PREFIX = (
    "## MiniMax H3 Fun ControlNet",
    "## Preparing the control video",
    "Krea 2 V10 full showcase",
    "Krea 2 V9 reference workflow",
    "# Edit Prompt Enhancer",
    "You are H3 V28.2 Director",
)
# 文件级白名单：整文件为"官方规范/上游模板/自研规则文本"，其中的长段落属于工程文档
DOC_FILES = {
    "custom_nodes/local_author/8197_production_line/H3_Prompt_Sidecar/frozen_h3_rules.md",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/official-minimax-h3-prompt/SKILL.md",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/official-minimax-h3-prompt/references/base-en.txt",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/official-minimax-h3-prompt/references/ref-en.txt",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/h3-v28-2-director/SKILL.md",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/h3-v28-2-director/references/physical-feasibility.md",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/h3-v28-2-director/references/structured-plan.md",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/v28_director_prompts.py",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/v28_prompt_compiler.py",
    "custom_nodes/local_author/8197_production_line/H3_V28_Director/v28_schemas.py",
}

TEXT_EXT = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".js", ".mjs",
            ".cjs", ".html", ".css", ".ps1", ".bat", ".cmd", ".sh", ".ini", ".cfg"}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache"}

# .py 源文件用 AST 取"字符串字面量"，不取代码正文/注释：
# 代码正文里出现 pose/scene/camera 这类词是命名与文档字符串，不是创作提示词。
CODE_EXT = {".py"}
JS_EXT = {".js", ".mjs", ".cjs"}
DOC_EXT = {".md", ".txt", ".rst"}
JSON_EXT = {".json"}
# 真正的 JS 字面量（含转义），而不是「两个引号之间的任意代码」：
# 旧写法 "..."{500,} 会把一段代码正文当成字符串切片，产生整批假阳性。
JS_LITERAL = re.compile(
    r"\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'|`(?:[^\\`]|\\.)*`", re.S)
# 代码/CSS 正文的特征标记：出现即说明这段文本是被程序消费的代码，不是创作提示词
CODE_MARKS = re.compile(
    r"[{};]|\bfunction\b|=>|\bconst\b|\bvar\b|\blet\b|\breturn\b|\.append\("
    r"|document\.|\.style\b|querySelector|addEventListener")


def iter_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)
    elif isinstance(obj, str):
        yield obj


def public_text_files(root=ROOT):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            ext = os.path.splitext(f)[1].lower()
            if ext in TEXT_EXT or ext == "":
                rel = os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")
                out.append((rel, ext))
    return sorted(out)


def candidate_strings(rel, ext, text):
    """按文件类型选作用域，保证"长创作段落"能被单独评估而不把代码正文当提示词。"""
    if ext in JSON_EXT:
        try:
            data = json.loads(text)
        except Exception:
            return None  # 交回结构门禁裁决；本测试记账为"未解析"
        return list(iter_strings(data))
    if ext in CODE_EXT:
        import ast
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return None
        return [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and len(n.value) >= MIN_LEN]
    if ext in JS_EXT:
        out = []
        for m in JS_LITERAL.finditer(text):
            s = m.group(0)[1:-1]
            if len(s) < MIN_LEN:
                continue
            # 含代码/CSS 结构标记的长字面量是被程序消费的正文，不是创作提示词
            if len(CODE_MARKS.findall(s)) >= 3:
                continue
            out.append(s)
        return out
    if ext in DOC_EXT:
        return [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def prompt_score(s):
    """把"提示词形状"量化：创作词汇命中数 + 负向提示词特征 + 描述符堆叠。"""
    kw = len(KEYWORDS.findall(s))
    neg = len(NEG_SIGNS.findall(s))
    desc = bool(DESCRIPTOR_RUN.search(s))
    return kw + (3 if neg >= 3 else 0) + (4 if desc else 0)


def is_documented_template(s):
    return any(s.lstrip().startswith(d) for d in DOC_PREFIX)


def looks_like_personal_prompt(s):
    if len(s) < MIN_LEN or PLACEHOLDER.search(s) or is_documented_template(s):
        return False
    return prompt_score(s) >= 4


def _scan(violations, sig_hits, unparsed, root=ROOT):
    for rel, ext in public_text_files(root):
        p = os.path.join(root, rel.replace("/", os.sep))
        try:
            raw = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        cands = candidate_strings(rel, ext, raw)
        if cands is None:
            unparsed.append(rel)
            continue
        # (1) 已知个人签名：对每个候选字符串的 MD5 判定（作用于全树内容，不限于工作流）
        for s in cands:
            if hashlib.md5(s.encode("utf-8", "replace")).hexdigest()[:8] in PERSONAL_SIGNATURES:
                sig_hits.append((rel, s[:40]))
        if rel in DOC_FILES:
            continue
        # (2) 规则扫描：提示词形状的长文本
        for s in cands:
            if looks_like_personal_prompt(s):
                violations.append((rel, s[:60]))


def test_no_personal_prompt_residue():
    violations, sig_hits, unparsed = [], [], []
    _scan(violations, sig_hits, unparsed)
    assert not sig_hits, "已知个人创作提示词签名复现: %s" % sig_hits[:5]
    assert not unparsed, "内容无法解析导致扫描被跳过（尺坏即非 PASS）: %s" % unparsed[:5]
    assert not violations, "发现个人创作提示词残留:\n" + "\n".join(
        "  %s | %s" % (v[0], v[1]) for v in violations[:20])
    return len(public_text_files()), len(DOC_FILES)


# ---------------------------------------------------------------- 尺子有没有牙
# 一把从不报警的尺和一把被改坏的尺长得一样。植入样本必须报警，模板与代码必须不报警。
# 样本用短片段运行时拼接：任何单个字面量都 < MIN_LEN，因此本测试文件自身不会被自己扫出来。
_PLANTED_PARTS = [
    "A photorealistic young woman in a beige linen dress, soft window lighting, ",
    "warm cinematic composition, natural skin texture, loose hair, relaxed posture, ",
    "slow camera push in, detailed face, realistic body figure, cozy bedroom background, ",
    "gentle facial expression, subtle gesture, intimate scene, high detail. ",
    "Negative: extra woman, duplicate limbs, deformed hands, blurry face, worst quality, ",
    "low quality, cloned body, unwanted character, extra fingers.",
]
PLANTED_PERSONAL_PROMPT = "".join(_PLANTED_PARTS * 3)


def test_ruler_has_teeth():
    assert len(PLANTED_PERSONAL_PROMPT) >= MIN_LEN, "植入样本长度不足，测不到形状判定"
    # 正控制 1：形状判定必须命中植入的提示词样本
    assert looks_like_personal_prompt(PLANTED_PERSONAL_PROMPT), "尺子失效：植入提示词未被识别"
    # 正控制 2：端到端——把植入样本放进一棵假树，_scan 必须产出违规
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="h3_ruler_")
    try:
        d = os.path.join(tmp, "workflows", "current")
        os.makedirs(d)
        io.open(os.path.join(d, "planted.json"), "w", encoding="utf-8").write(
            json.dumps({"nodes": [{"type": "N", "prompt": PLANTED_PERSONAL_PROMPT}]},
                       ensure_ascii=False))
        v, s, u = [], [], []
        _scan(v, s, u, root=tmp)
        assert v, "尺子失效：植入到假工作流里的个人提示词没被端到端检出"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # 正控制 3：签名表真的在工作——把植入样本的 MD5 临时当作已知签名，必须命中
    planted_md5 = hashlib.md5(PLANTED_PERSONAL_PROMPT.encode("utf-8")).hexdigest()[:8]
    keep = set(PERSONAL_SIGNATURES)
    PERSONAL_SIGNATURES.add(planted_md5)
    try:
        tmp2 = tempfile.mkdtemp(prefix="h3_ruler_sig_")
        try:
            os.makedirs(os.path.join(tmp2, "workflows"))
            io.open(os.path.join(tmp2, "workflows", "x.json"), "w", encoding="utf-8").write(
                json.dumps({"a": PLANTED_PERSONAL_PROMPT}))
            v2, s2, u2 = [], [], []
            _scan(v2, s2, u2, root=tmp2)
            assert s2, "尺子失效：已知签名通道对匹配字符串无反应"
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)
    finally:
        PERSONAL_SIGNATURES.clear()
        PERSONAL_SIGNATURES.update(keep)
    # 负控制 A：带 <Subject N> 的通用模板不得报警
    template = ("<Subject 1> stands in the scene with soft lighting and a slow camera move. "
                + "photorealistic lighting camera composition body face hair scene ") * 12
    assert not looks_like_personal_prompt(template), "尺子过火：带 <Subject N> 的通用模板被判私人内容"
    # 负控制 B：JS/CSS 代码正文不得进入候选（旧版正则会把代码当字符串切片，整批假阳性）
    code_text = "const CSS = `" + "div{background:#111; color:#eee}\n" * 60 + "`;"
    cands = candidate_strings("web/a.js", ".js", code_text)
    assert cands == [], "尺子过火：CSS/代码正文被当成创作提示词候选"
    return True


def main():
    checks = [("test_no_personal_prompt_residue", test_no_personal_prompt_residue),
              ("test_ruler_has_teeth", test_ruler_has_teeth)]
    bad = []
    for name, fn in checks:
        try:
            fn()
            print("  PASS  %s" % name)
        except AssertionError as e:
            bad.append(name)
            print("  FAIL  %s\n        %s" % (name, str(e)[:600]))
    if bad:
        print("\n结果：%d 通过 / %d 失败" % (len(checks) - len(bad), len(bad)))
        return 1
    n_files, n_doc = test_no_personal_prompt_residue()
    print("PASS: 全树 %d 个文本文件（%d 个工程文档走文件级白名单）无个人创作提示词残留"
          "，且尺子经植入样本自证有效 —— PERSONAL_PROMPT_RESIDUE=0" % (n_files, n_doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
