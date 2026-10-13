# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""Read the pinned official Ref2VA guide; validate format without rewriting.

Official-guide dependency (changed 2026-10-13)
----------------------------------------------
This module reads MiniMax's official ``references/ref-en.txt`` to derive the six
section titles and the retention-marker enums. Those files were proven to be
verbatim upstream originals and were removed from this repository because their
redistribution licence is unresolved (``LICENSE_HOLD`` — see
``skills/official-minimax-h3-prompt/README.md``).

They are now an **external, user-installed dependency**. Resolution order:

  1. ``$H3_MINIMAX_OFFICIAL_SKILL_DIR``  (a directory containing
     ``references/ref-en.txt``)
  2. ``<package>/skills/official-minimax-h3-prompt/`` (installed in place)
  3. otherwise -> :class:`H3OfficialGuideMissing` with an actionable message.

The module stays *importable* without the guide: the constants are resolved
lazily on first use, so ``import v28_h3_format`` (and therefore
``v28_manual_continuation`` and the whole test suite) never explodes at import
time, while the first real validation reports the missing dependency explicitly
instead of degrading into a bare ``FileNotFoundError`` or, worse, silently
passing.
"""
from pathlib import Path
import os
import re

# The six section titles are also pinned independently by this project's own
# compiler (v28_director_core.SECTIONS / v28_prompt_compiler.SECTIONS). They are
# kept here as the *fallback contract* so the six-segment director keeps working
# when the official guide is not installed. They are NOT a substitute for the
# official marker enums (TASK_TYPES / VISIBLE_MARKERS / AUDIO_MARKERS), which
# can only come from the official file.
SECTION_CONTRACT = ("subject_definitions", "summary", "retention_analysis",
                    "detailed_description", "overall_soundscape", "non_diegetic_music")

ENV_SKILL_DIR = "H3_MINIMAX_OFFICIAL_SKILL_DIR"

_GUIDE_REL = os.path.join("references", "ref-en.txt")
_PKG_SKILL_DIR = Path(__file__).resolve().parent / "skills" / "official-minimax-h3-prompt"

INSTALL_HINT = (
    "python scripts/setup/install_minimax_official_skill.py --source <你的 MiniMax-H3 本地副本>\n"
    "  或设置环境变量 {env} 指向一个含 {rel} 的目录。\n"
    "  注意：该文件的再分发授权尚未取得（LICENSE_HOLD），本仓库不自动下载、不捆绑。\n"
    "  详见 custom_nodes/.../H3_V28_Director/skills/official-minimax-h3-prompt/README.md"
).format(env=ENV_SKILL_DIR, rel=_GUIDE_REL)


class H3OfficialGuideMissing(RuntimeError):
    """Raised when the official MiniMax H3 guide cannot be located.

    Deliberately not ``FileNotFoundError``: the message has to name the missing
    dependency, the paths already tried and the exact install command, so an
    operator can fix it without reading the source.
    """


def candidate_guide_dirs() -> list:
    """Every directory that may hold the official guide, in resolution order."""
    out = []
    env = os.environ.get(ENV_SKILL_DIR, "").strip()
    if env:
        out.append(Path(env))
    out.append(_PKG_SKILL_DIR)
    return out


def resolve_guide_path():
    """Return the guide path, or ``None`` when the dependency is not installed."""
    for d in candidate_guide_dirs():
        p = d / _GUIDE_REL
        if p.is_file():
            return p
    return None


def official_guide_status() -> dict:
    """Machine-readable status of the external dependency (for tests / ops)."""
    path = resolve_guide_path()
    tried = [str(d / _GUIDE_REL) for d in candidate_guide_dirs()]
    if path is None:
        return {"state": "MISSING", "path": None, "tried": tried,
                "env": ENV_SKILL_DIR, "action": INSTALL_HINT}
    return {"state": "PRESENT", "path": str(path), "tried": tried,
            "env": ENV_SKILL_DIR, "action": None}


def _require_guide() -> Path:
    p = resolve_guide_path()
    if p is None:
        st = official_guide_status()
        raise H3OfficialGuideMissing(
            "缺少 MiniMax 官方提示词指南（外部依赖）\n"
            "  需要文件: %s\n"
            "  已尝试路径:\n    %s\n"
            "  安装方式:\n    %s" % (_GUIDE_REL, "\n    ".join(st["tried"]), INSTALL_HINT))
    return p


_GUIDE_CACHE = {}


def _load_guide() -> dict:
    """Parse the official guide once; cache the derived vocabularies."""
    if _GUIDE_CACHE:
        return _GUIDE_CACHE
    guide = _require_guide()
    text = guide.read_text(encoding="utf-8")

    sections = tuple(re.findall(r"^\| `([a-z_]+)` \|", text, re.M)[:6])
    if len(sections) != 6:
        raise RuntimeError("官方 Ref2VA guide 的六段结构无法读取：%s" % guide)
    if sections != SECTION_CONTRACT:
        # Not a hard failure: the official order changed upstream. Surface it.
        raise RuntimeError(
            "官方六段标题与本项目契约不一致：官方=%s 契约=%s（%s）"
            % (list(sections), list(SECTION_CONTRACT), guide))

    def _values(start, end):
        if start not in text or end not in text:
            raise RuntimeError(
                "官方 guide 缺少定位标记（%r / %r），无法提取枚举；文件可能不是官方版本：%s"
                % (start, end, guide))
        part = text.split(start, 1)[1].split(end, 1)[0]
        values = frozenset(re.findall(r"^\| `([a-z_ ]+)` \|", part, re.M))
        if not values:
            raise RuntimeError(
                "官方 guide 的 %r~%r 区间内没有解析到枚举行，文件可能不是官方版本：%s"
                % (start, end, guide))
        return values

    _GUIDE_CACHE.update({
        "GUIDE": guide,
        "SECTIONS": sections,
        "TASK_TYPES": _values("Choose task types according", "## 4."),
        "VISIBLE_MARKERS": _values("### 4.1", "### 4.2"),
        "AUDIO_MARKERS": _values("### 4.2", "## 5."),
    })
    return _GUIDE_CACHE


def __getattr__(name):
    """Lazy access to the guide-derived constants (PEP 562).

    Keeps ``import v28_h3_format`` working when the official guide is absent,
    while ``v28_h3_format.SECTIONS`` still raises the explicit
    ``H3OfficialGuideMissing`` the moment it is actually needed.
    """
    if name in ("GUIDE", "SECTIONS", "TASK_TYPES", "VISIBLE_MARKERS", "AUDIO_MARKERS"):
        return _load_guide()[name]
    if name == "OFFICIAL_SKILL":
        return _PKG_SKILL_DIR
    raise AttributeError("module %r has no attribute %r" % (__name__, name))


LABEL = re.compile(r"<(Subject|Picture|Video|Audio)\s+(\d+)>")


def parse_sections(text: str) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("完整基础 Prompt 不能为空")
    sections = _load_guide()["SECTIONS"]
    pattern = r"^\s*(" + "|".join(sections) + r"):[ \t]*\r?$"
    matches = list(re.finditer(pattern, text, re.M))
    if tuple(m.group(1) for m in matches) != sections:
        raise ValueError("必须按官方顺序填写且仅填写一次全部六段标题")
    return {m.group(1): text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)].strip()
            for i, m in enumerate(matches)}


def _block(text: str, key: str) -> str:
    try:
        return parse_sections(text).get(key.rstrip(":"), "")
    except ValueError:
        return ""


def looks_compiled(text: str) -> bool:
    try:
        parse_sections(text)
        return True
    except ValueError:
        return False


class OfficialH3FormatValidator:
    """Validate the pinned guide against a concrete reference/runtime contract."""
    def audit(self, text, *, reference_contract=None, duration_seconds=None,
              segment_id=None, generation_mode=None, shots_expected=None):
        G = _load_guide()
        SECTIONS = G["SECTIONS"]
        TASK_TYPES = G["TASK_TYPES"]
        VISIBLE_MARKERS = G["VISIBLE_MARKERS"]
        AUDIO_MARKERS = G["AUDIO_MARKERS"]
        try: sections = parse_sections(text)
        except ValueError as exc: return [str(exc)]
        errors = []
        if any(not sections[k] for k in SECTIONS): errors.append('六段内容不能为空；无内容请明确N/A')
        prefix = re.match(r'^\[([^\]]+)\]', sections['summary'])
        tasks = [x.strip() for x in prefix[1].split('+')] if prefix else []
        if not tasks or any(x not in TASK_TYPES for x in tasks): errors.append('TASK_TYPE_AMBIGUOUS: summary必须明确合法官方任务类型')
        if len(tasks) != len(set(tasks)): errors.append('任务类型不可重复')
        dd = sections['detailed_description']
        shots = list(re.finditer(r'\[Shot\s+(\d+)\]', dd))
        if not shots or [int(x[1]) for x in shots] != list(range(1,len(shots)+1)):
            errors.append('Shot编号必须从1连续且唯一')
        if shots_expected is not None and len(shots) != shots_expected: errors.append('Shot数量与实际合同不一致')
        last = -1
        for i, shot in enumerate(shots):
            tail = dd[shot.end():]
            stamp = re.match(r'\s*At\s+(\d{2}):(\d{2})\.(\d{3}),', tail)
            if i == 0:
                if re.match(r'\s*At\s+\d',tail): errors.append('Shot 1不能带cut timestamp')
            elif not stamp: errors.append(f'Shot {shot[1]}缺少At MM:SS.mmm,切点')
            else:
                seconds = int(stamp[1])*60 + int(stamp[2]) + int(stamp[3])/1000
                if int(stamp[2]) >= 60 or seconds <= last or seconds <= 0: errors.append('Shot切点必须格式有效且严格递增')
                if duration_seconds is not None and seconds >= duration_seconds: errors.append('Shot切点超出实际segment duration')
                last = seconds
        declarations = set()
        for line in sections['subject_definitions'].splitlines():
            m = re.match(r'\s*(<(?:Subject|Picture|Video|Audio)\s+\d+>)',line)
            if m:
                if m[1] in declarations: errors.append('引用定义不可重复：'+m[1])
                declarations.add(m[1])
        source_pictures = {f'<Picture {n}>' for kind,n in LABEL.findall(sections['subject_definitions']) if kind=='Picture'}
        for kind,number in LABEL.findall(text):
            label = f'<{kind} {number}>'
            if label not in declarations and not (kind=='Picture' and label in source_pictures): errors.append('悬空引用：'+label)
        for line in sections['retention_analysis'].splitlines():
            m = re.match(r'\s*<(Subject|Picture|Video|Audio)\s+\d+>(?:\s*\([^)]*\))?\s*:\s*([a-z_]+)',line)
            if line.strip()!='N/A' and (not m or m[2] not in (AUDIO_MARKERS if m[1]=='Audio' else VISIBLE_MARKERS)):
                errors.append('retention marker与reference类型不匹配：'+line[:90])
            if re.search(r'\(S\d+\)',line): errors.append('retention_analysis不得赋speaker ID')
        tokens = list(re.finditer(r'</?d>', text))
        opened = False
        for m in tokens:
            if (m[0]=='<d>') == opened: errors.append('对白d标签嵌套或闭合错误')
            opened = m[0]=='<d>'
        if opened: errors.append('对白d标签未闭合')
        speaker_bindings, speaker_order = {}, []
        previous = 0
        for dialogue in re.finditer(r'<d>(.*?)</d>',dd,re.S):
            language = re.match(r'\s*\[([A-Za-z][A-Za-z -]{1,45})\]',dialogue[1])
            if not language or re.search(r'shot|reference|editing|continuation|reuse',language[1],re.I):
                errors.append('对白缺少有效[Language]，不能用Shot/Task标签代替')
            prefix_text = dd[max(previous,dialogue.start()-250):dialogue.start()]
            speakers = list(re.finditer(r'(?:<Subject\s+(\d+)>\s*)?\(S(\d+)\)',prefix_text))
            copied_audio = '<Audio ' in prefix_text and any(x in sections['retention_analysis'] for x in ('fully_copy','partially_copy'))
            if not speakers and not copied_audio: errors.append('对白缺少明确speaker ID，如<Subject 1> (S1)')
            if speakers:
                subject,speaker = speakers[-1].groups()
                binding = subject or 'voice:'+speaker
                if binding in speaker_bindings and speaker_bindings[binding] != speaker: errors.append('speaker ID漂移')
                if speaker in speaker_bindings.values() and speaker_bindings.get(binding) != speaker: errors.append('speaker ID绑定冲突')
                speaker_bindings[binding] = speaker
                if speaker not in speaker_order: speaker_order.append(speaker)
            previous = dialogue.end()
        if speaker_order and [int(x) for x in speaker_order] != list(range(1,len(speaker_order)+1)):
            errors.append('speaker按实际发声顺序从S1编号')
        if reference_contract is not None:
            c = reference_contract
            labels = {int(n) for kind,n in LABEL.findall(text) if kind=='Picture'}
            actual = {int(r['h3_picture']) for r in c['active_reference_index']}
            if labels != actual: errors.append('Picture标签与实际ReferenceContract不一致')
            for kind in ('Audio','Video'):
                used = {int(n) for k,n in LABEL.findall(text) if k==kind}
                allowed = set(c.get('media_labels',{}).get(kind,[]))
                if 'media_labels' in c and used-allowed: errors.append(f'{kind}引用没有真实对应输入')
            if segment_id != c['segment_id'] or generation_mode != c['generation_mode']: errors.append('validator运行段号/模式与合同不一致')
            if duration_seconds != c['duration_seconds']: errors.append('validator时长与合同不一致')
        return list(dict.fromkeys(errors))

    def warnings(self, text):
        return ['正文含非英文原文；保留用户语言，不自动翻译'] if re.search(r'[\u4e00-\u9fff]',text) else []


VALIDATOR = OfficialH3FormatValidator()
def audit_prompt(text, *, reference_contract=None, duration_seconds=None, segment_id=None,
                 generation_mode=None, shots_expected=None):
    return VALIDATOR.audit(text, reference_contract=reference_contract, duration_seconds=duration_seconds,
        segment_id=segment_id, generation_mode=generation_mode, shots_expected=shots_expected)


def complete_base_format(text: str) -> str:
    """Insert missing Ref2VA task/shot/language markers; retain every input byte.

    Only simplified manual uses this boundary. Six-section ambiguity, broken
    dialogue delimiters and unidentified languages remain explicit errors.
    """
    sections = parse_sections(text)
    if not re.match(r"\[(?:keyframe completion|reference generation|video editing|video continuation|audio reuse|audio reference)(?:[^\]]*)\]", sections['summary']):
        if sections['summary'].startswith('['):
            raise ValueError('summary 任务类型标签无法识别，请明确官方任务类型')
        raise ValueError('TASK_TYPE_AMBIGUOUS: 请明确summary的官方任务类型，系统不能猜reference generation/编辑/续写')
    if '[Shot 1]' not in sections['detailed_description'] and not re.search(r'\[Shot\s+\d+\]', sections['detailed_description']):
        match = re.search(r"^\s*detailed_description:[ \t]*\r?$", text, re.M)
        text = text[:match.end()] + '\n[Shot 1]' + text[match.end():]

    def dialogue(match):
        original = match.group(1)
        if re.match(r'\s*\[[^\]]+\]', original): return match[0]
        # A nearby explicit language takes precedence over written-script detection.
        context = text[max(0, match.start()-160):match.start()]
        declared = re.findall(r'\b(?:in|language\s*:)\s+(Mandarin|Chinese|English|Cantonese|Japanese|Korean|French|Spanish|German|Russian)\b', context, re.I)
        if declared: language = declared[-1].capitalize()
        else: raise ValueError('对白缺少语言说明，请在 <d> 内填写明确的 [Language] 标签；对白原文未修改')
        return '<d>[' + language + ']' + original + '</d>'
    return re.sub(r'<d>(.*?)</d>', dialogue, text, flags=re.S)


def render(sections: dict) -> str:
    return "\n\n".join(f"{key}:\n{sections[key]}" for key in _load_guide()["SECTIONS"])
