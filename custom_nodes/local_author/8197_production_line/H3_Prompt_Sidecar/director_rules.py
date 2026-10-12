# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""Pure H3 formatting/quality rules. No files, model transport or execution integration."""

from __future__ import annotations

import json,re

LEDGER_MAX_EVENTS = 12            # completed_events 上限，禁止无限增长

LEDGER_MAX_DIALOGUE = 6           # recent_dialogue 上限，只防重复

LEDGER_MAX_THREADS = 8            # open_threads 上限

SECTION_RE = tuple(
    ("subject_definitions", "summary", "retention_analysis",
     "detailed_description", "overall_soundscape", "non_diegetic_music"))

MEDIA_RE = re.compile(r"<(Picture|Audio|Video|Subject)\s*(\d+)>", re.I)

def _declared_resources(*texts: str) -> set[str]:
    declared = set()
    for t in texts:
        for m in MEDIA_RE.finditer(t or ""):
            declared.add(f"{m.group(1).capitalize()} {m.group(2)}")
    return declared

def _undeclared_refs(text: str, declared: set[str]) -> list[str]:
    used = {f"{m.group(1).capitalize()} {m.group(2)}"
            for m in MEDIA_RE.finditer(text or "")}
    return sorted(used - declared)

ZH_MARK = "===ZH==="

EN_MARK = "===EN==="

STATE_MARK = "===STATE==="   # 一次调用同时产出 candidate_state_delta（任务书第十一节）

_SYSTEM_IDENTITY = "你是 MiniMax H3 (Ref2VA) 提示词编译器。继承全局设定与连续性账本，编译本段中英文提示词和结束状态。"

_RESOURCE_RULES = "两稿只能引用输入明确声明的 <Picture N>/<Audio N>/<Video N>/<Subject N>；禁止新增未声明资源。"

_AUDIO_RULES = "<REDACTED_USER_PROMPT>"

_OUTPUT_RULES = """本次仅编译一个短片段，不展开整部电影。最多2个镜头、6句新对白；不重复对白或段落。一次只返回合法 JSON：english_prompt、chinese_prompt、state_delta。不要代码围栏或解释。
english_prompt 和 chinese_prompt 每稿必须包含以下六个独占行标题，顺序固定，不得遗漏：
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
每个标题下面才是正文。detailed_description 必须写本段从当前状态开始的实际镜头、动作、结束位置及对白。
<REDACTED_USER_PROMPT>
global settings 的图片初始姿态只用于参考，current_end_state 是本段真实开始状态。
guide 中的资源标签只是规则范例，不构成资源声明。只能使用 global settings、账本、本段delta中声明的标签。
state_delta.end_state 必须反映本段动作完成后的状态，不得复制开始状态（例如照片已放桌上就不能仍持在手中）。
<REDACTED_USER_PROMPT>
open_threads 写尚可继续发展的方向。无需重列已解决问题。"""

_COMPILER_RULES = '<REDACTED_USER_PROMPT>'

OUTPUT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["english_prompt", "chinese_prompt", "state_delta"],
    "properties": {
        "english_prompt": {"type": "string"}, "chinese_prompt": {"type": "string"},
        "state_delta": {"type": "object", "additionalProperties": False,
            "required": ["end_state", "new_completed_events", "new_dialogue", "open_threads"],
            "properties": {
                "end_state": {"type": "object", "additionalProperties": False,
                    "required": ["人物位置", "人物姿势", "服装", "场景", "人物关系", "关键道具", "进行中的动作"],
                    "properties": {key: {"type": "string"} for key in
                        ["人物位置", "人物姿势", "服装", "场景", "人物关系", "关键道具", "进行中的动作"]}},
                "new_completed_events": {"type": "array", "items": {"type": "string"}},
                "new_dialogue": {"type": "array", "maxItems": 6, "items": {"type": "string", "maxLength": 240}},
                "open_threads": {"type": "array", "items": {"type": "string"}}}}}}

def build_messages(gset, guide, ledger, delta, head):
    # Exact invariant ordering. No timestamps, IDs, hashes, counters or state before boundary.
    prefix = (_SYSTEM_IDENTITY + "\n\n【H3蒸馏规则】\n" + guide + "\n" + _COMPILER_RULES
              + "\n\n【global settings】\n" + gset
              + "\n\n【resource规则】\n" + _RESOURCE_RULES
              + "\n\n【audio reference规则】\n" + _AUDIO_RULES
              + "\n\n【输出schema】\n" + _OUTPUT_RULES
              + "\n" + json.dumps(OUTPUT_SCHEMA, ensure_ascii=False, sort_keys=True))
    dynamic = "\n\n".join("【" + key + "】\n" + json.dumps(ledger.get(key, default), ensure_ascii=False)
        for key, default in [("current_end_state", {}), ("completed_events", []),
                             ("recent_dialogue", []), ("open_threads", [])])
    allowed = sorted(_declared_resources(gset, json.dumps(ledger, ensure_ascii=False), delta))
    dynamic += "\n\n【本段用户delta】\n" + head + delta.strip()
    dynamic += "\n本次资源白名单（guide 示例标签不算声明）：" + "、".join(allowed)
    dynamic += "<REDACTED_USER_PROMPT>"
    return [{"role": "system", "content": prefix}, {"role": "user", "content": dynamic}]

def parse_model_output(raw):
    try:
        obj = json.loads(_strip_fence(raw))
        state = obj["state_delta"]
        if not isinstance(state["end_state"], dict) or not all(isinstance(k, str) and isinstance(v, str) for k,v in state["end_state"].items()):
            raise ValueError("invalid end_state")
        for key in ("new_completed_events", "new_dialogue", "open_threads"):
            if not isinstance(state[key], list) or not all(isinstance(v, str) for v in state[key]):
                raise ValueError("invalid " + key)
        if len(state["new_dialogue"]) > 6 or any(len(line)>240 for line in state["new_dialogue"]):
            raise ValueError("dialogue array exceeds bounds")
        if not state["end_state"] or not state["new_completed_events"]:
            raise ValueError("state must contain a new event and an end state")
        return obj["chinese_prompt"].strip(), obj["english_prompt"].strip(), state
    except (ValueError, KeyError, TypeError, AttributeError):
        return "", "", {}

def normalize_output(raw, delta):
    """Deterministic formatting only; no extra inference or invented story state."""
    zh, en, candidate = parse_model_output(raw)
    if not candidate:
        return raw
    def ordered(text):
        matches = list(re.finditer(r"^\s*(" + "|".join(SECTION_RE) + r"):[ \t]*", text, re.M))
        if len(matches) != 6 or {m.group(1) for m in matches} != set(SECTION_RE):
            return text
        parts = {m.group(1): text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].strip()
                 for i,m in enumerate(matches)}
        return "\n\n".join(key + ":\n" + parts[key] for key in SECTION_RE)
    zh, en = ordered(zh), ordered(en)
    dialogue_re = re.compile(r"<d>\s*(?:\[[^\]]+\]\s*)?(.*?)</d>", re.S)
    spoken_en = dialogue_re.findall(en)
    spoken_zh = dialogue_re.findall(zh)
    # Restore explicitly supplied dialogue only when both drafts and state give an unambiguous single line.
    quoted = re.findall(r'“([^”]+)”', delta)
    if (len(quoted) == len(spoken_en) == len(spoken_zh) == 1
            and candidate["new_dialogue"] == quoted):
        def restore(match):
            return "<d>[Chinese] " + quoted[0] + "</d>"
        en = dialogue_re.sub(restore, en)
        zh = dialogue_re.sub(restore, zh)
        spoken_en = spoken_zh = quoted
    # Dialogue ledger must contain only what the final two drafts actually say.
    if spoken_en == spoken_zh:
        candidate["new_dialogue"] = spoken_en
    return json.dumps({"english_prompt": en, "chinese_prompt": zh, "state_delta": candidate}, ensure_ascii=False)

def _sections_ok(text: str) -> bool:
    found = tuple(m.group(1) for m in re.finditer(
        r"^\s*(" + "|".join(SECTION_RE) + r"):[ \t]*\r?$", text, re.M))
    return found == SECTION_RE

def _strip_fence(s: str) -> str:
    """去掉模型偶尔加的 ```lang / ``` 包裹，不改变正文内容。"""
    s = s.strip()
    if s.startswith("```"):
        nl = s.find("\n")
        if nl > 0:
            s = s[nl + 1:]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()

_MAX_TAIL_CLOSERS = 8   # a sane JSON can never be missing more than this many trailing closers

def json_tail_repair(text: str):
    """仅尾部括号缺失的确定性修复（作者裁决 2026-10-04）。

    唯一允许的情形：所有字符串都已闭合、主体完整、只是末尾少了若干
    闭合括号 `}` / `]`。此时按扫描栈精确补齐缺失的闭合符并返回补齐后
    的文本；调用方必须重新 json.loads 验证。不调用模型、不修改正文。

    任何其它缺陷（字符串未闭合、括号错配、多余闭合符、深度异常）一律
    返回 None，由调用方如实报错，绝不冒充成功。"""
    stack = []
    in_string = False
    escaped = False
    for ch in text:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack:
                return None                       # 多余闭合符：结构错误，不修
            closer = "}" if stack.pop() == "{" else "]"
            if ch != closer:
                return None                       # 括号错配：结构错误，不修
    if in_string or escaped:
        return None                               # 字符串未闭合：不是纯尾部问题
    if not stack or len(stack) > _MAX_TAIL_CLOSERS:
        return None                               # 没有缺失，或缺失异常多：不修
    return text + "".join("}" if c == "{" else "]" for c in reversed(stack))


_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

EMPTY_LEDGER = {
    "current_end_state": {},   # 人物位置/姿势/服装/场景/关系/关键道具/进行中的动作
    "completed_events": [],    # 已发生、禁止机械重复的重要事件（有上限）
    "recent_dialogue": [],         # <REDACTED_USER_PROMPT>
    "open_threads": [],        # 未解决问题/发展中的冲突/未完成事件/可推进方向
}

AUTO_CONTINUE_PATTERNS = (
    "继续", "继续剧情", "继续推进", "接着演", "接着上一段", "往下发展",
    "自行推进", "自行推进剧情", "继续发展", "接着演，多说点话", "接着演,多说点话",
    # 自然变体（实测必需：只列字面词会把「继续推进剧情」这类等价说法漏掉，
    # 导致明明是自动续写却走 NORMAL 分支，浪费了 open_threads 推进机制）
    "继续推进剧情", "继续往下", "继续发展剧情", "接着演下去",
    "继续剧情发展", "剧情继续", "继续演", "接着来", "继续吧", "往下演",
)

_AUTO_SUFFIX = ("吧", "呀", "啊", "哦", "喔", "了")

def is_auto_continue(delta: str) -> bool:
    """判定是否 AUTO_CONTINUE（任务书第十二节）。

    收紧口径：**整条指令去掉标点后必须与某个触发词完全相等**才成立。
    这样「继续说：她走到窗边」这类含具体内容的长指令会正确落到 NORMAL 分支，
    不会被误当成"没给内容、让模型自己编"的自动续写。
    """
    compact = re.sub(r"[\s，,。.、！!？?：:；;]+", "", (delta or "").strip())
    if not compact:
        return False
    triggers = {re.sub(r"[\s，,。.、！!？?：:；;]+", "", p) for p in AUTO_CONTINUE_PATTERNS}
    if compact in triggers:
        return True
    # 允许纯语气后缀（"继续吧" / "接着演呀"），但仍要求其余部分与触发词完全相等，
    # 这样"继续说：她走到窗边"不会因为含"继续"而被误判。
    return any(compact == t + sfx for t in triggers for sfx in _AUTO_SUFFIX)

def _as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if x not in (None, "")]
    return [v]

def commit_ledger(ledger: dict, delta_obj: dict) -> dict:
    """把 candidate_state_delta 合并进正式账本（带上限裁剪，防无限增长）。"""
    out = {
        "current_end_state": delta_obj.get("end_state") or ledger.get("current_end_state", {}),
        "completed_events": (list(ledger.get("completed_events", []))
                             + _as_list(delta_obj.get("new_completed_events")))[-LEDGER_MAX_EVENTS:],
        "recent_dialogue": (list(ledger.get("recent_dialogue", []))
                            + _as_list(delta_obj.get("new_dialogue")))[-LEDGER_MAX_DIALOGUE:],
        "open_threads": (list(ledger.get("open_threads", []))
                         + _as_list(delta_obj.get("open_threads")))[-LEDGER_MAX_THREADS:],
    }
    return out

def _zh_ratio(text: str) -> tuple[int, int, float]:
    """返回 (汉字数, 拉丁字母数, 汉字占比)。先剥资源标签与节名，避免它们压低比值。"""
    body = MEDIA_RE.sub(" ", text or "")
    body = re.sub(r"(" + "|".join(SECTION_RE) + r")\s*:", " ", body)
    cjk = len(_CJK_RE.findall(body))
    letters = len(re.findall(r"[A-Za-z]", body))
    return cjk, letters, cjk / max(cjk + letters, 1)

_ZH_SECTION_MIN = 0.25      # 整篇阈值（原有）

_ZH_PER_SECTION_MIN = 0.15  # 单段阈值

def _zh_bad_sections(zh: str) -> list[str]:
    """找出**逐段**没中文化的段名。

    实测（2026-10-02 D1）：整篇 ratio 20.9% 触发拦截，但真正原因是
    detailed_description 整段写成了英文（0% 中文），其余 5 段都是真中文
    （74% / 82.5% / 42.5%）。只报整篇比例会让重试无从下手，必须指出是哪一段。

    ★ 短内容豁免（实测踩到）：官方格式允许 `non_diegetic_music: N/A` 这类
      合法极短内容，纯 N/A 段不该被判成"没本地化"。只有当段落**有实质内容**
      （剥离标签/节名后 ≥20 个可见字符）才做比例判定。
    """
    NA_TOKENS = {"", "n/a", "na", "none", "无", "不适用", "无音乐", "无配乐"}
    bad = []
    parts = re.split(r"^(" + "|".join(SECTION_RE) + r")\s*:", zh or "", flags=re.M)
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i + 1]
        # 剥掉资源标签后再看剩余实质内容
        visible = MEDIA_RE.sub(" ", body)
        visible = re.sub(r"\[(Shot\s*\d+|[^\]]*)\]", " ", visible)
        visible = re.sub(r"\b(S\d+)\b", " ", visible)
        visible = re.sub(r"\s+", " ", visible).strip()
        if len(visible) < 20:
            continue                       # 合法短段（N/A 之类），跳过判定
        cjk, letters, ratio = _zh_ratio(body)
        if cjk == 0 or ratio < _ZH_PER_SECTION_MIN:
            bad.append(f"{name}（汉字占比 {ratio:.0%}）")
    return bad

def _zh_is_chinese(zh: str, en: str) -> tuple[bool, str]:
    """中文稿必须是真中文：汉字占比达标，且不得与英文稿逐字相同。

    这是硬校验。仅检查六段结构会漏过「把英文稿原样复制一份当中文稿」这种假通过
    （2026-10-02 实测：zh_sha == en_sha、六段齐全、valid=True 的假合格）。
    """
    if not zh:
        return False, "中文稿为空"
    cjk, letters, ratio = _zh_ratio(zh)
    if cjk == 0:
        return False, "中文稿里没有任何汉字，实际写成了英文（中文稿必须是中文正文）"
    bad_secs = _zh_bad_sections(zh)
    if bad_secs:
        return False, ("以下段落没有真正本地化成中文：" + "、".join(bad_secs)
                       + f"（整篇汉字占比 {ratio:.0%}）。必须逐段用中文重写，"
                         "<REDACTED_USER_PROMPT>")
    if ratio < _ZH_SECTION_MIN:
        return False, f"中文稿汉字占比过低（{ratio:.0%}），正文没有真正本地化成中文"
    if zh.strip() == en.strip():
        return False, "中文稿与英文稿逐字相同，属于把英文稿复制了一份充当中文对照稿"
    return True, ""

# One model call returns required section bodies; the public API still exposes
# complete English/Chinese prompt strings. No semantic reconstruction.
for key in ("english_prompt", "chinese_prompt"):
    OUTPUT_SCHEMA["properties"][key] = {"type":"object", "additionalProperties":False, "required":list(SECTION_RE),
        "properties":{section:{"type":"string", "minLength":1} for section in SECTION_RE}}
_OUTPUT_RULES = """一次返回JSON，包含english_prompt、chinese_prompt、state_delta。
english_prompt和chinese_prompt各是六字段对象，字段严格为subject_definitions、summary、retention_analysis、detailed_description、overall_soundscape、non_diegetic_music。
每个字段只填本节正文，不重复节名，不写其它节。服务端会按六段顺序添加标题；最终稿仍严格符合官方六段式。
本段最多2镜头、6句新对白，不重复句子。detailed_description英文正文约350–500词，中文必须完整对应，不能缺少实际动作、镜头、时间线、结束位置。
两稿的<d>对白保留用户原语言、逐字一致。只引用输入中明确声明的资源标签。
state_delta只记录本段结束状态、新完成事件、新对白与待推进线索，不复制已确认历史。"""
