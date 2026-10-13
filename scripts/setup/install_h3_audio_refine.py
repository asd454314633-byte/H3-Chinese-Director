#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install the external H3 audio-refinement component (third-party, MIT).

Upstream : https://github.com/Adudeguyman/ComfyUI-H3-AudioRefine
Author   : Adudeguyman
Licence  : MIT (GitHub API license.spdx_id == "MIT", verified 2026-10-13)
Pinned   : commit fd5a8dfe8b4c636b1877abd07d11ebc985eddbed (2026-09-06T22:47:23Z)
           nodes.py git blob 4b8e966f330cb96dfab75b9aeab5ae952c236972

`H3_AudioUpgrade/nodes.py` calls `H3AudioRefineSampler` from this pack. The pack
is third-party and is NOT redistributed inside this repository, so it must be
installed separately. This script copies it from a source you provide, keeps the
upstream MIT `LICENSE` next to it (a licence obligation of MIT), and verifies the
blob SHA1 against the pinned commit.

Usage
-----
    python scripts/setup/install_h3_audio_refine.py --source <克隆目录>
    python scripts/setup/install_h3_audio_refine.py --verify          # 只校验
    python scripts/setup/install_h3_audio_refine.py --source ... --dest <目标目录>

Exit codes: 0 OK / 2 verify failed / 3 missing --source / 4 configuration error.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

UPSTREAM = "https://github.com/Adudeguyman/ComfyUI-H3-AudioRefine"
PINNED_COMMIT = "fd5a8dfe8b4c636b1877abd07d11ebc985eddbed"
PINNED_BLOB = "4b8e966f330cb96dfab75b9aeab5ae952c236972"

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
DEFAULT_DEST = (REPO_ROOT / "custom_nodes" / "local_author" / "8197_production_line"
                / "H3_AudioUpgrade" / "vendor")


def _load_status(dest: Path):
    """Reuse the runtime loader's own status() so install and runtime agree."""
    sys.path.insert(0, str(dest.parent))
    import importlib
    mod = importlib.import_module("audio_refine_loader")
    return mod, mod.status()


def verify(dest: Path) -> int:
    if not (dest / "nodes.py").is_file():
        print("FAIL     vendor/nodes.py 缺失：%s" % (dest / "nodes.py"), file=sys.stderr)
        return 2
    mod, st = _load_status(dest)
    print("OK       vendor_dir=%s" % st["vendor_dir"])
    print("OK       blob_sha1=%s" % st["blob_sha1"])
    print("%s 与钉住提交 %s 的 blob %s %s"
          % ("OK      " if st["matches_pinned_commit"] else "WARN    ",
             PINNED_COMMIT[:12], PINNED_BLOB,
             "一致" if st["matches_pinned_commit"] else "不一致（版本漂移）"))
    if not st["has_license"]:
        print("FAIL     vendor/LICENSE 缺失 —— MIT 要求随附版权与许可声明", file=sys.stderr)
        return 2
    print("OK       vendor/LICENSE 存在")
    return 0


def install(src: Path, dest: Path) -> int:
    nodes = src / "nodes.py"
    if not nodes.is_file():
        print("ERROR: 源目录中没有 nodes.py：%s" % nodes, file=sys.stderr)
        return 3
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(nodes, dest / "nodes.py")
    print("copied   nodes.py <- %s" % nodes)
    lic = src / "LICENSE"
    if lic.is_file():
        shutil.copy2(lic, dest / "LICENSE")
        print("copied   LICENSE  <- %s" % lic)
    else:
        print("WARN     源目录没有 LICENSE；MIT 要求保留版权与许可声明，"
              "请自行补上（上游：%s）" % UPSTREAM, file=sys.stderr)
    # optional upstream docs, never required
    for extra in ("README.md", "TECHNICAL.md"):
        if (src / extra).is_file():
            shutil.copy2(src / extra, dest / extra)
            print("copied   %s <- %s" % (extra, src / extra))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="本地 Adudeguyman/ComfyUI-H3-AudioRefine 副本")
    ap.add_argument("--dest", default=str(DEFAULT_DEST))
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)

    dest = Path(a.dest)
    if a.verify:
        return verify(dest)
    if not a.source:
        print("ERROR: --source 必填（本脚本不自动下载）。\n"
              "  git clone %s\n  python scripts/setup/install_h3_audio_refine.py --source <克隆目录>"
              % UPSTREAM, file=sys.stderr)
        return 3
    rc = install(Path(a.source), dest)
    if rc:
        return rc
    rc = verify(dest)
    if rc:
        return rc
    print("\nInstalled to %s" % dest)
    print("Runtime env (optional):  H3_AUDIO_REFINE_DIR=%s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
