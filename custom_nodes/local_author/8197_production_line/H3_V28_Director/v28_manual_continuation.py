# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""Local structural compilation. User deltas are always embedded verbatim."""
import copy
import re
from . import v28_h3_format as F
from . import v28_reference_contract as RC

MODE = "MANUAL_CONTINUATION"
LEDGER_FILE = "ACCEPTED_STATE_LEDGER.json"
STATE_FIELDS = ("position", "orientation", "pose", "held_objects", "scene",
                "clothing", "camera_endpoint", "completed_actions", "dialogue_events")
_PERSISTENT = re.compile(r"从(?:现在|这(?:一)?段)开始|后面都|之后一直")
_STATIC = re.compile(r"固定(?:机位|镜头)|static camera|locked.off", re.I)


class ManualContinuationCompiler:
    def __init__(self, base_prompt: str, reference_mapping: list[dict]):
        self.reference_mapping = reference_mapping
        self.base = F.complete_base_format(base_prompt)
        self.sections = F.parse_sections(self.base)
        errors = F.audit_prompt(self.base)
        if errors:
            raise ValueError("基础 Prompt 格式错误：" + "; ".join(errors))
        candidates = {"女人": [], "男人": []}
        for number, description in re.findall(r"<Subject\s+(\d+)>\s*([^\n]+)", self.sections["subject_definitions"]):
            if re.search(r"\bwoman\b|女人|女子", description, re.I):
                candidates["女人"].append(f"<Subject {number}>")
            if re.search(r"\bman\b|男人|男子", description, re.I):
                candidates["男人"].append(f"<Subject {number}>")
        self.aliases = {key: values[0] for key, values in candidates.items() if len(set(values)) == 1}
        self.invariants = {k: self.sections[k] for k in
                           ("subject_definitions", "retention_analysis", "overall_soundscape", "non_diegetic_music")}
        dd = self.sections["detailed_description"]
        # Only explicitly descriptive sentences become fixed visual facts.
        self.invariants["visual"] = "\n".join(s.strip() for s in re.split(r"(?<=[.!?。])\s+|\n", dd)
            if re.search(r"clothing|wears|hair|glasses|lighting|background|visual style|do not|must never|服装|发型|眼镜|光照|背景|禁止|不得", s, re.I))

    def advance(self, previous: dict, text: str) -> dict:
        state = copy.deepcopy(previous)
        positions = state.setdefault("position", {})
        # Explicit destinations only; unsupported clauses remain in endpoint_text.
        position_events = []
        for match in re.finditer(r"(女人|女子|男人|男子|她|他|<Subject\s+\d+>)(?:从[^，。；\n]{0,20}?)?(?:走到|走向|跑到|来到|站到|坐到)([^，。；\n]{1,20})", text):
            actor, destination = match.groups()
            alias = {"女子": "女人", "她": "女人", "男子": "男人", "他": "男人"}.get(actor, actor)
            label = self.aliases.get(alias, actor)
            position_events.append((match.start(), label, destination))
        for match in re.finditer(r"(<Subject\s+\d+>|The woman|The man)\s+(?:walks?|moves?|runs?)\s+(?:from .{1,35}?\s+)?(?:to|toward)\s+([^.!\n]{1,40})", text, re.I):
            actor, destination = match.groups()
            label = self.aliases.get("女人" if actor.lower() == "the woman" else "男人", actor) if not actor.startswith("<") else actor
            position_events.append((match.start(), label, destination))
        for match in re.finditer(r"(<Subject\s+\d+>|The woman|The man)\s+(?:sits?|stands?|is seated|is standing)\s+(?:on|near|at|beside|in)\s+([^.!\n]{1,40})", text, re.I):
            actor, place = match.groups()
            label = self.aliases.get("女人" if actor.lower() == "the woman" else "男人", actor) if not actor.startswith("<") else actor
            position_events.append((match.start(), label, place))
        for _, label, destination in sorted(position_events):
            positions[label] = destination
        for field, pattern in (("orientation", r"(?:朝向|面向)([^，。；\n]+)"),
                               ("pose", r"(?:站起|坐下|转身|躺下|跪下)"),
                               ("held_objects", r"(?:拿着|握着|持有)([^，。；\n]+)"),
                               ("scene", r"(?:场景变为|场景：)([^，。；\n]+)"),
                               ("clothing", r"(?:换上|服装：)([^，。；\n]+)")):
            hits = list(re.finditer(pattern, text))
            if hits:
                state[field] = hits[-1].group(0)
        state["completed_actions"] = text
        state["dialogue_events"] = re.findall(r"[“\"]([^”\"]*)[”\"]", text)
        state["endpoint_text"] = text
        return state

    def compile(self, inputs: list[str], clocks: list[dict], ledger: dict | None = None) -> tuple[list[str], list[dict]]:
        if len(inputs) != len(clocks) or any(not isinstance(x, str) or not x.strip() for x in inputs):
            raise ValueError(f"请填写基础 Prompt 和全部 {len(clocks)-1} 段剧情增量")
        ledger = ledger or {}
        accepted = {int(x["segment_id"]): x for x in ledger.get("entries", [])}
        state = {key: "UNKNOWN" for key in STATE_FIELDS}
        state["position"] = {}
        state = self.advance(state, self.sections["detailed_description"])
        state["clothing"] = self.invariants["visual"] or "As declared in subject_definitions."
        persistent = {}
        baseline_camera = "Continue the established camera geometry."
        texts, receipts, reference_rows = [], [], None
        for i, (text, clock) in enumerate(zip(inputs, clocks), 1):
            before = copy.deepcopy(state)
            if i == 1:
                final = self.base
            else:
                camera = persistent.get("camera", baseline_camera)
                scope = "LOCAL_OVERRIDE"
                static_matches = [m for m in _STATIC.finditer(text)
                    if not re.search(r"不要|不得|禁止|不使用|非|not|never|without", text[max(0, m.start()-12):m.start()], re.I)]
                if static_matches:
                    camera = "Static camera for this segment."
                    if _PERSISTENT.search(text):
                        scope = "PERSISTENT_OVERRIDE"
                        persistent["camera"] = camera
                duration = clock["end_time"] - clock["start_time"]
                end_stamp = f"{int(duration // 60):02d}:{duration % 60:06.3f}"
                origin = "; ".join(f"{actor} at {pos}" for actor, pos in before.get("position", {}).items())
                carried = [str(before[key]) for key in ("orientation", "pose", "held_objects", "scene", "clothing") if before.get(key) not in (None, "UNKNOWN", "")]
                continuity = "; ".join([origin] + carried).strip("; ") or "Established spatial and body endpoint of the preceding segment; its completed events are not repeated."
                sections = {key: self.sections[key] for key in F.SECTIONS}
                for key in ("subject_definitions", "retention_analysis"):
                    sections[key] = "\n".join("Initial-segment-only reference (already fulfilled): " + line
                        if re.search(r"first frame|0\.0+ seconds|首帧", line, re.I) else line
                        for line in sections[key].splitlines())
                sections["summary"] = self.sections['summary'].split(']',1)[0] + '] Continue the established subjects and the explicitly selected references for this segment.'
                sections["detailed_description"] = (
                    f"[Shot 1] Duration {duration:g} seconds. Start from the preceding endpoint: {continuity}\n"
                    + (f"Fixed visual facts: {self.invariants['visual']}\n" if self.invariants["visual"] else "")
                    + f"Camera: {camera}\n[00:00-{end_stamp}]\n" + text)
                final = F.render(sections)
                if text not in final:
                    raise ValueError("用户原文完整性校验失败")
                state = self.advance(before, text)
                state["camera_endpoint"] = camera
            contract = RC.draft(final, self.reference_mapping, mode=MODE, segment_id=i,
                duration=clock['end_time']-clock['start_time'], role_input=None if i==1 else text, previous=reference_rows)
            reference_rows = contract['reference_decisions']
            final = contract['canonical_prompt']
            if i in accepted:
                if accepted[i].get('source_canonical_prompt', accepted[i]["canonical_prompt"]) != final:
                    raise ValueError(f"已接受第 {i} 段不可被新草稿覆盖")
                state = copy.deepcopy(accepted[i]["end_state"])
                persistent = copy.deepcopy(accepted[i]["persistent_overrides"])
            errors = F.audit_prompt(final, reference_contract=contract, duration_seconds=contract['duration_seconds'], segment_id=i, generation_mode=MODE)
            if errors:
                raise ValueError("官方结构校验失败：" + "; ".join(errors))
            texts.append(final)
            receipts.append({"segment_id": i, "start_state": before, "end_state": copy.deepcopy(state),
                             "persistent_overrides": copy.deepcopy(persistent), "canonical_prompt": final,
                             "user_delta": text if i > 1 else "", "accepted": i in accepted,
                             'reference_contract': contract})
        return texts, receipts
