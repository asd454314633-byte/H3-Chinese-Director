# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""8197 H3 startup policy: lower only the pinned-memory registration cap.

Gate repair (2026-10-13, G-1)
-----------------------------
The previous published copy compared against a hard-coded sanitisation
placeholder path (see the audit report for the exact literal)::

    _expected = Path(<placeholder>)        # <- never a real directory
    if args.port == 8197 and Path(mm.__file__).resolve() == _expected.resolve():
        ...apply...

``_expected`` could never equal any real path, so the branch was **dead**: the
policy could never apply and, worse, it never said so. That is a fake gate — it
looks like a guard, and it reports nothing when it cannot guard.

The instance identity now comes from configuration, and an unconfigured/missing
identity is reported loudly instead of degrading into silence:

    H3_MEMORY_POLICY_COMFY_ROOT   absolute path to the ComfyUI root whose
                                  comfy.model_management this policy may patch

Behaviour:
  * unset / empty / not absolute -> ``logging.error`` NOT_APPLIED (never silent),
    and :func:`self_check` reports ``CONFIG_MISSING``;
  * set but the running instance is not that root, or the port is not 8197
    -> ``logging.warning`` SKIPPED with the reason;
  * set and matching -> apply, then log the before/after values.

No public copy may reintroduce a literal local path here.
"""
import logging
import os
from pathlib import Path

from comfy.cli_args import args
import comfy.model_management as mm

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

#: Env var that supplies the instance identity. Required; there is no default,
#: because a wrong default is exactly what made this gate fake.
ENV_COMFY_ROOT = "H3_MEMORY_POLICY_COMFY_ROOT"

#: Reasons reported by :func:`self_check`; kept importable so tests can assert
#: the gate is real without booting ComfyUI with a wrong path.
STATE_APPLIED = "APPLIED"
STATE_SKIPPED = "SKIPPED"
STATE_NOT_APPLIED = "NOT_APPLIED"
STATE_CONFIG_MISSING = "CONFIG_MISSING"
STATE_CONFIG_INVALID = "CONFIG_INVALID"


def _configured_root() -> tuple[str, Path | None]:
    """(state, resolved root). Never invents a path."""
    raw = os.environ.get(ENV_COMFY_ROOT, "").strip()
    if not raw:
        return STATE_CONFIG_MISSING, None
    p = Path(raw)
    if not p.is_absolute():
        return STATE_CONFIG_INVALID, p
    return "", p


def self_check(port=None, mm_file=None) -> dict:
    """Evaluate the gate without side effects; used by tests and by startup.

    Returns a dict with ``state`` and ``reason``. The real startup path calls
    :func:`apply` which performs the mutation; this function never mutates.
    """
    port = args.port if port is None else port
    mm_file = Path(mm.__file__) if mm_file is None else Path(mm_file)

    state, root = _configured_root()
    if state == STATE_CONFIG_MISSING:
        return {"state": state, "reason": "%s 未配置；无法确定目标实例，拒绝静默降级" % ENV_COMFY_ROOT}
    if state == STATE_CONFIG_INVALID:
        return {"state": state, "reason": "%s 必须是绝对路径，当前=%r" % (ENV_COMFY_ROOT, str(root))}
    if port != 8197:
        return {"state": STATE_SKIPPED, "reason": "端口 %s != 8197，非目标实例" % port}
    try:
        same = mm_file.resolve() == (root / "comfy" / "model_management.py").resolve()
    except OSError as exc:
        return {"state": STATE_CONFIG_INVALID,
                "reason": "无法解析 %s：%s" % (ENV_COMFY_ROOT, exc)}
    if not same:
        return {"state": STATE_SKIPPED,
                "reason": "运行实例不是 %s 指向的实例" % ENV_COMFY_ROOT}
    if args.disable_pinned_memory or mm.MAX_PINNED_MEMORY <= 0:
        return {"state": STATE_NOT_APPLIED, "reason": "pinned memory 已禁用"}
    if mm.TOTAL_PINNED_MEMORY != 0:
        return {"state": STATE_NOT_APPLIED, "reason": "pin 初始化已开始"}
    return {"state": STATE_APPLIED, "reason": "",
            "before_gib": mm.MAX_PINNED_MEMORY / 1024**3,
            "after_gib": min(mm.MAX_PINNED_MEMORY, 16 * 1024**3) / 1024**3}


def apply() -> dict:
    """Run the gate and mutate ``mm.MAX_PINNED_MEMORY`` when it passes."""
    res = self_check()
    if res["state"] == STATE_CONFIG_MISSING or res["state"] == STATE_CONFIG_INVALID:
        # Explicit failure, not a silent no-op.
        logging.error("[H3 MemoryPolicy] NOT_APPLIED: %s（设置 %s 后重启实例）",
                      res["reason"], ENV_COMFY_ROOT)
        return res
    if res["state"] == STATE_SKIPPED:
        logging.warning("[H3 MemoryPolicy] SKIPPED: %s", res["reason"])
        return res
    if res["state"] == STATE_NOT_APPLIED:
        logging.warning("[H3 MemoryPolicy] NOT_APPLIED: %s", res["reason"])
        return res

    _old = mm.MAX_PINNED_MEMORY
    _new = min(_old, 16 * 1024**3)
    mm.MAX_PINNED_MEMORY = _new
    logging.info('[H3 MemoryPolicy] Pinned memory cap: %.6f GiB -> %.6f GiB; MAX_PINNED_MEMORY=%d; TOTAL_PINNED_MEMORY=%d; TOTAL_RAM=%d',
                 res["before_gib"], res["after_gib"], mm.MAX_PINNED_MEMORY,
                 mm.TOTAL_PINNED_MEMORY, mm.ram)
    return res


apply()
