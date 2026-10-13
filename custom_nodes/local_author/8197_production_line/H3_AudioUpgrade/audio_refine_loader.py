# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""Resolve the external H3 audio-refinement dependency with a diagnosable failure.

Background
----------
``H3_AudioUpgrade/nodes.py`` needs ``H3AudioRefineSampler``. It used to be a
relative import (``from .vendor.nodes import H3AudioRefineSampler``) but the
``vendor/`` directory was never published, so reaching that branch produced a
bare ``ModuleNotFoundError`` with no hint about what to install.

The component is **third-party**, not authored here:

  * upstream : https://github.com/Adudeguyman/ComfyUI-H3-AudioRefine
  * author   : Adudeguyman
  * licence  : MIT (GitHub API ``license.spdx_id == "MIT"``, verified 2026-10-13)
  * pinned   : commit ``fd5a8dfe8b4c636b1877abd07d11ebc985eddbed`` (2026-09-06T22:47:23Z)
               ``nodes.py`` git blob SHA1 ``4b8e966f330cb96dfab75b9aeab5ae952c236972``
               (14753 B LF-normalised; SHA256
               ``1e2cc221dfc65ea453150e250188b2b57cc77a2bc916481db0c2a2f395604bd1``)
  * its own  : ``LICENSE`` = "MIT License / Copyright (c) 2026 Adudeguyman"

It is therefore installed **separately**, from its own upstream, and this module
is the single place that locates it. Missing -> :class:`H3AudioRefineMissing`
naming the dependency, the paths tried, the pinned coordinates and the install
command. Never a silent skip, never a fabricated implementation.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path

ENV_VENDOR_DIR = "H3_AUDIO_REFINE_DIR"

UPSTREAM = "https://github.com/Adudeguyman/ComfyUI-H3-AudioRefine"
UPSTREAM_AUTHOR = "Adudeguyman"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_COMMIT = "fd5a8dfe8b4c636b1877abd07d11ebc985eddbed"
UPSTREAM_BLOB_SHA1 = "4b8e966f330cb96dfab75b9aeab5ae952c236972"
UPSTREAM_NODES_SHA256_LF = "1e2cc221dfc65ea453150e250188b2b57cc77a2bc916481db0c2a2f395604bd1"

_PKG_DIR = Path(__file__).resolve().parent
_CLASS_NAME = "H3AudioRefineSampler"

INSTALL_HINT = (
    "  git clone {url}\n"
    "  然后把仓库放到 {env} 指向的目录（或直接放到 {default}），\n"
    "  也可以用随包脚本：python scripts/setup/install_h3_audio_refine.py --source <克隆目录>"
).format(url=UPSTREAM, env=ENV_VENDOR_DIR, default=str(_PKG_DIR / "vendor"))


class H3AudioRefineMissing(RuntimeError):
    """The external audio-refinement component is not installed.

    Raised instead of ``ModuleNotFoundError`` so the operator learns *what* is
    missing, *where* it was looked for, and *how* to install it. The audio
    refinement pass is never silently skipped.
    """


def candidate_vendor_dirs() -> list:
    out = []
    env = os.environ.get(ENV_VENDOR_DIR, "").strip()
    if env:
        out.append(Path(env))
    out.append(_PKG_DIR / "vendor")
    return out


def resolve_vendor_dir():
    """Return the directory holding the upstream ``nodes.py``, or ``None``."""
    for d in candidate_vendor_dirs():
        if (d / "nodes.py").is_file():
            return d
    return None


def _blob_sha1(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def status() -> dict:
    """Machine-readable status of the external dependency (for tests / ops)."""
    tried = [str(d / "nodes.py") for d in candidate_vendor_dirs()]
    d = resolve_vendor_dir()
    if d is None:
        return {"state": "MISSING", "vendor_dir": None, "tried": tried,
                "env": ENV_VENDOR_DIR, "action": INSTALL_HINT}
    nodes = d / "nodes.py"
    blob = _blob_sha1(nodes)
    return {
        "state": "PRESENT",
        "vendor_dir": str(d),
        "tried": tried,
        "env": ENV_VENDOR_DIR,
        "blob_sha1": blob,
        "matches_pinned_commit": blob == UPSTREAM_BLOB_SHA1,
        "has_license": (d / "LICENSE").is_file(),
    }


def _load_from_dir(d: Path):
    """Import the upstream ``nodes.py`` as an isolated module (no package)."""
    mod_name = "_h3_audio_refine_vendor"
    path = d / "nodes.py"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise H3AudioRefineMissing("无法为 %s 构造 import spec" % path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    # Upstream nodes.py is a ComfyUI custom-node module: it only imports torch /
    # numpy / comfy internals, so executing it here is the same thing ComfyUI
    # does when it loads the pack from custom_nodes/.
    spec.loader.exec_module(mod)
    return mod


def load_sampler_class(strict: bool = True):
    """Return ``H3AudioRefineSampler``; raise :class:`H3AudioRefineMissing` if absent.

    ``strict=False`` returns ``None`` instead of raising, for callers that want
    to render an explicit UI-level message. It never falls back to a stub: an
    unverified substitute would silently change the audio output.
    """
    d = resolve_vendor_dir()
    if d is None:
        st = status()
        if not strict:
            return None
        raise H3AudioRefineMissing(
            "缺少外部音频精修组件（第三方依赖，未随本仓库分发）\n"
            "  需要: %s.nodes 提供的 %s\n"
            "  上游: %s\n"
            "  作者: %s    许可: %s\n"
            "  钉住版本: commit %s  nodes.py blob %s\n"
            "  已尝试路径:\n    %s\n"
            "  安装方式:\n%s" % ("vendor", _CLASS_NAME, UPSTREAM, UPSTREAM_AUTHOR,
                                 UPSTREAM_LICENSE, UPSTREAM_COMMIT, UPSTREAM_BLOB_SHA1,
                                 "\n    ".join(st["tried"]), INSTALL_HINT))
    try:
        mod = _load_from_dir(d)
    except Exception as exc:  # noqa: BLE001 - surfaced with context, never swallowed
        raise H3AudioRefineMissing(
            "已找到外部音频精修组件目录 %s，但导入失败：%s: %s" % (d, type(exc).__name__, exc)
        ) from exc
    cls = getattr(mod, _CLASS_NAME, None)
    if cls is None:
        raise H3AudioRefineMissing(
            "%s 中未找到 %s（上游接口已变化？）" % (d / "nodes.py", _CLASS_NAME))
    return cls
