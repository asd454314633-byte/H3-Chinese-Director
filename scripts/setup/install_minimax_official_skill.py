#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install the MiniMax official H3 prompt-writing skill from a LOCAL source.

Why this script exists
----------------------
`H3_V28_Director/skills/official-minimax-h3-prompt/` used to carry three
verbatim copies of MiniMax's official files (SKILL.md, references/base-en.txt,
references/ref-en.txt). The 2026-10-13 ownership audit proved they are upstream
originals (byte-identical after stripping the sanitisation banner and
normalising newlines) and that the upstream repository declares **no** open
source licence (`GitHub API license == null`; a Community License Agreement with
NOTICE / no-additional-terms / territory restrictions ships with the model
card). Redistribution is therefore on **HOLD** and the files were removed from
this repository.

This script deliberately does NOT download anything by default. It installs from
a source you already obtained yourself, and it verifies every file against the
pinned upstream blob SHA1 so a wrong/partial copy cannot pass silently.

Usage
-----
    # install from a local clone/extract of MiniMax-AI/MiniMax-H3
    python scripts/setup/install_minimax_official_skill.py --source D:\\src\\MiniMax-H3

    # verify an already-installed copy
    python scripts/setup/install_minimax_official_skill.py --verify

    # choose another destination (default: <repo>/.../skills/official-minimax-h3-prompt)
    python scripts/setup/install_minimax_official_skill.py --source ... --dest D:\\skills\\h3-prompt

    # opt-in network download (requires TWO explicit flags; prints the HOLD notice)
    python scripts/setup/install_minimax_official_skill.py --allow-download --i-have-license-rights

Exit codes: 0 = installed/verified OK, 2 = missing or mismatched files,
3 = missing --source, 4 = configuration error.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

# ---- pinned upstream coordinates -------------------------------------------
UPSTREAM_REPO = "MiniMax-AI/MiniMax-H3"
UPSTREAM_PREFIXES = (
    "skills/h3-prompt-writing",
    ".agents/skills/h3-prompt-writing",
    ".claude/skills/h3-prompt-writing",
)

# path-in-skill -> {relative size, git blob sha1 of the upstream content}
# NOTE: SKILL.md exists in two sizes upstream (2623 under skills/, 2177 under
# .agents/ and .claude/). We accept either, because both are official.
FILES = {
    "SKILL.md": {
        "rel": "SKILL.md",
        "blobs": {"b6d9b2839384a588763a9c24315225dd8ce19d56",
                  "066429d78f72b080a52350a5b165e52cb31b0bca"},
    },
    "references/base-en.txt": {
        "rel": "references/base-en.txt",
        "blobs": {"40cf586a634d677d6b7107b367cf0ec9621be728"},
    },
    "references/ref-en.txt": {
        "rel": "references/ref-en.txt",
        "blobs": {"7ae1b2d07d743fd2392258a96449be9e9e322d35"},
    },
}

HOLD_NOTICE = (
    "LICENSE_HOLD: MiniMax-AI/MiniMax-H3 declares no open source licence "
    "(GitHub API license == null). The Hugging Face model card ships a "
    "Community License Agreement requiring verbatim NOTICE on redistribution, "
    "forbidding additional terms, and excluding some territories. This "
    "repository does NOT hold a written redistribution grant. Install only if "
    "you have your own rights, and do not redistribute the installed files."
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
DEFAULT_DEST = (REPO_ROOT / "custom_nodes" / "local_author" / "8197_production_line"
                / "H3_V28_Director" / "skills" / "official-minimax-h3-prompt")


def blob_sha1(path: Path) -> str:
    """git blob SHA1 of `path` with LF-normalised content (matches upstream)."""
    raw = path.read_bytes()
    data = raw.replace(b"\r\n", b"\n")
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def find_in_source(src: Path, rel: str) -> Path | None:
    for prefix in UPSTREAM_PREFIXES:
        cand = src / prefix.replace("/", os.sep) / rel.replace("/", os.sep)
        if cand.is_file():
            return cand
    # tolerate a source that already points at the skill directory
    cand = src / rel.replace("/", os.sep)
    return cand if cand.is_file() else None


def verify(dest: Path) -> tuple[list[str], list[str]]:
    ok, bad = [], []
    for rel, meta in FILES.items():
        p = dest / rel.replace("/", os.sep)
        if not p.is_file():
            bad.append("MISSING  %s" % rel)
            continue
        got = blob_sha1(p)
        if got in meta["blobs"]:
            ok.append("%s  blob=%s" % (rel, got))
        else:
            bad.append("MISMATCH %s  blob=%s (expected one of %s)"
                       % (rel, got, sorted(meta["blobs"])))
    return ok, bad


def install(src: Path, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    for rel in FILES:
        found = find_in_source(src, rel)
        if found is None:
            print("ERROR: source does not contain %s (looked under %s)"
                  % (rel, ", ".join(UPSTREAM_PREFIXES)), file=sys.stderr)
            return 3
        target = dest / rel.replace("/", os.sep)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found, target)
        print("copied   %-28s <- %s" % (rel, found))
    return 0


def download(dest: Path) -> int:
    """Opt-in only. Prints the HOLD notice before touching the network."""
    import urllib.request
    print(HOLD_NOTICE)
    dest.mkdir(parents=True, exist_ok=True)
    for rel in FILES:
        url = ("https://raw.githubusercontent.com/%s/main/skills/h3-prompt-writing/%s"
               % (UPSTREAM_REPO, rel))
        target = dest / rel.replace("/", os.sep)
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=60) as r:
            target.write_bytes(r.read())
        print("downloaded %-28s <- %s" % (rel, url))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="local copy of MiniMax-AI/MiniMax-H3")
    ap.add_argument("--dest", default=str(DEFAULT_DEST), help="installation directory")
    ap.add_argument("--verify", action="store_true", help="verify only, do not install")
    ap.add_argument("--allow-download", action="store_true")
    ap.add_argument("--i-have-license-rights", action="store_true")
    a = ap.parse_args(argv)

    dest = Path(a.dest)

    if a.verify:
        ok, bad = verify(dest)
        for line in ok:
            print("OK       " + line)
        for line in bad:
            print("FAIL     " + line, file=sys.stderr)
        print("MINIMAX_OFFICIAL_SKILL = %s (%d/%d files verified)"
              % ("PRESENT" if not bad else "INCOMPLETE", len(ok), len(FILES)))
        return 0 if not bad else 2

    if a.allow_download:
        if not a.i_have_license_rights:
            print("ERROR: --allow-download requires --i-have-license-rights.",
                  file=sys.stderr)
            return 4
        rc = download(dest)
    else:
        if not a.source:
            print(HOLD_NOTICE)
            print("\nERROR: --source is required (this script never downloads by "
                  "default). Obtain the official files yourself, then re-run.",
                  file=sys.stderr)
            return 3
        src = Path(a.source)
        if not src.is_dir():
            print("ERROR: --source is not a directory: %s" % src, file=sys.stderr)
            return 3
        rc = install(src, dest)
    if rc:
        return rc

    ok, bad = verify(dest)
    for line in ok:
        print("OK       " + line)
    for line in bad:
        print("FAIL     " + line, file=sys.stderr)
    if bad:
        return 2
    print("\nInstalled to %s" % dest)
    print("Exports:  set H3_MINIMAX_OFFICIAL_SKILL_DIR=%s" % dest)
    print(HOLD_NOTICE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
