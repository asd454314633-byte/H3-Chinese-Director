# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""8197 H3 startup policy: lower only the pinned-memory registration cap."""
import logging
from pathlib import Path
from comfy.cli_args import args
import comfy.model_management as mm

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_expected = Path(r'<REDACTED_LOCAL_PATH>/D')
if args.port == 8197 and Path(mm.__file__).resolve() == _expected.resolve():
    if args.disable_pinned_memory or mm.MAX_PINNED_MEMORY <= 0:
        logging.warning('[H3 MemoryPolicy] NOT_APPLIED: pinned memory is disabled')
    elif mm.TOTAL_PINNED_MEMORY != 0:
        logging.error('[H3 MemoryPolicy] NOT_APPLIED: pin initialization already started')
    else:
        _old = mm.MAX_PINNED_MEMORY
        _new = min(_old, 16 * 1024**3)
        mm.MAX_PINNED_MEMORY = _new
        logging.info('[H3 MemoryPolicy] Pinned memory cap: %.6f GiB -> %.6f GiB; MAX_PINNED_MEMORY=%d; TOTAL_PINNED_MEMORY=%d; TOTAL_RAM=%d',
                     _old / 1024**3, _new / 1024**3, mm.MAX_PINNED_MEMORY,
                     mm.TOTAL_PINNED_MEMORY, mm.ram)
