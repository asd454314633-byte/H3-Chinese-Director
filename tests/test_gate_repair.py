#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gate-repair regression tests (2026-10-13).

Every test here targets a gate that was *fake* in the previous published copy:
it looked like a guard but could never fail, or it degraded silently instead of
reporting. Each test proves the gate can now actually bite, using a controlled
temporary directory and, where it matters, a deliberate violation (positive
control). A gate that cannot detect a planted violation is reported as FAIL, not
as PASS.

    G-1  H3_MemoryPolicy.disabled  — placeholder path made the guard dead code
    G-2  tests/_v28_bootstrap      — four identical placeholders made the
                                     anti-pollution comparison always equal
    G-3  H3_V28_Director/v28_paths — a placeholder was used as a real directory
    D-1  H3_AudioUpgrade           — missing third-party vendor raised a bare
                                     ModuleNotFoundError
    D-2  H3_V28_Director/v28_h3_format — missing MiniMax official guide

Nothing in here writes to the frozen production tree.

Direct run:  python tests/test_gate_repair.py
"""
from __future__ import annotations

import ast
import importlib.util
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PK = ROOT / "custom_nodes" / "local_author" / "8197_production_line"
V28 = PK / "H3_V28_Director"

PLACEHOLDER = "<REDACTED_LOCAL_PATH>/D"


def load_by_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_paths_module():
    """v28_paths with no configuration at all (the unconfigured baseline)."""
    for k in ("v28_paths",):
        sys.modules.pop(k, None)
    return load_by_path("v28_paths", V28 / "v28_paths.py")


# --------------------------------------------------------------------- G-3
class TestProjectDirIsNeverAPlaceholder(unittest.TestCase):
    """`PROJECT_DIR = Path('<REDACTED_LOCAL_PATH>/D')` must never come back."""

    def test_unconfigured_paths_hold_a_sentinel_not_a_placeholder(self):
        P = load_paths_module()
        self.assertTrue(P.unconfigured_paths(),
                        "unconfigured import should report its missing roots")
        for key in ("COMFY_ROOT", "PROJECTS_ROOT", "PROJECT_DIR"):
            self.assertNotIn("<REDACTED", str(getattr(P, key)),
                             "%s 又把脱敏占位符当成了路径" % key)

    def test_ensure_dirs_refuses_to_create_anything_when_unconfigured(self):
        P = load_paths_module()
        cwd = Path(tempfile.mkdtemp(prefix="h3_gate_cwd_"))
        old = os.getcwd()
        os.chdir(cwd)
        try:
            with self.assertRaises(P.H3PathConfigError) as ctx:
                P.ensure_dirs()
            msg = str(ctx.exception)
            self.assertIn("H3_COMFY_ROOT", msg)
            self.assertIn("H3_V28_PROJECTS", msg)
            # the whole point: nothing was created next to the working directory
            self.assertEqual(sorted(os.listdir(cwd)), [],
                             "ensure_dirs() 在未配置时仍然建了目录")
        finally:
            os.chdir(old)
            shutil.rmtree(cwd, ignore_errors=True)

    def test_atomic_write_refuses_too(self):
        P = load_paths_module()
        with self.assertRaises(P.H3PathConfigError):
            P.atomic_write_text(Path("x.json"), "{}")

    def test_configured_paths_make_the_gate_pass(self):
        """Positive control: with real roots, ensure_dirs actually works."""
        root = Path(tempfile.mkdtemp(prefix="h3_gate_ok_"))
        os.environ["H3_COMFY_ROOT"] = str(root / "comfy_root")
        os.environ["H3_V28_PROJECTS"] = str(root / "projects")
        try:
            P = load_paths_module()
            self.assertEqual(P.unconfigured_paths(), [])
            self.assertTrue(P.PATHS_CONFIGURED)
            P.ensure_dirs()
            self.assertTrue(P.DIRECTOR_LOGS_DIR.is_dir())
        finally:
            os.environ.pop("H3_COMFY_ROOT", None)
            os.environ.pop("H3_V28_PROJECTS", None)
            shutil.rmtree(root, ignore_errors=True)
            load_paths_module()  # restore module state for other tests

    def test_placeholder_env_value_is_rejected(self):
        os.environ["H3_COMFY_ROOT"] = PLACEHOLDER
        try:
            with self.assertRaises(Exception):
                load_paths_module()
        finally:
            os.environ.pop("H3_COMFY_ROOT", None)


# --------------------------------------------------------------------- G-2
class TestAntiPollutionGateCanActuallyFail(unittest.TestCase):
    """The watch list must be real, distinct, and able to detect a violation."""

    def setUp(self):
        self.B = load_by_path(
            "_v28_bootstrap", V28 / "tests" / "_v28_bootstrap.py")

    def test_unconfigured_watch_list_refuses_to_run(self):
        os.environ.pop(self.B.ENV_WATCH_PATHS, None)
        with self.assertRaises(self.B.H3AuditWatchConfigError) as ctx:
            self.B.watched_paths()
        self.assertIn(self.B.ENV_WATCH_PATHS, str(ctx.exception))

    def test_collapsed_watch_list_is_rejected(self):
        """Four identical placeholders was the original defect."""
        os.environ[self.B.ENV_WATCH_PATHS] = os.pathsep.join([PLACEHOLDER] * 4)
        try:
            with self.assertRaises(self.B.H3AuditWatchConfigError):
                self.B.watched_paths()
        finally:
            os.environ.pop(self.B.ENV_WATCH_PATHS, None)

    def test_single_entry_is_rejected(self):
        root = tempfile.mkdtemp(prefix="h3_gate_w_")
        os.environ[self.B.ENV_WATCH_PATHS] = root
        try:
            with self.assertRaises(self.B.H3AuditWatchConfigError):
                self.B.watched_paths()
        finally:
            os.environ.pop(self.B.ENV_WATCH_PATHS, None)
            shutil.rmtree(root, ignore_errors=True)

    def test_positive_control_a_planted_write_is_detected(self):
        """The gate must catch a deliberate violation in a temp directory."""
        root = Path(tempfile.mkdtemp(prefix="h3_gate_pollute_"))
        a, b = root / "projects", root / "h3_context"
        a.mkdir()
        b.mkdir()
        os.environ[self.B.ENV_WATCH_PATHS] = os.pathsep.join([str(a), str(b)])
        try:
            before = self.B.fingerprint_all()
            self.assertEqual(len(before), 2)
            self.assertEqual(self.B.detect_pollution(before, before), [])

            # deliberate violation: a test leaking into the watched tree
            (b / "clip_00001.safetensors").write_bytes(b"x" * 17)

            after = self.B.fingerprint_all()
            found = self.B.detect_pollution(before, after)
            self.assertTrue(found, "反污染门禁抓不到故意植入的写入 —— 门禁无效")
            self.assertTrue(any("h3_context" in f for f in found),
                            "报告里应点名被污染的目录：%s" % found)

            # and a file-content change inside a watched dir is caught too
            before2 = self.B.fingerprint_all()
            (b / "clip_00001.safetensors").write_bytes(b"y" * 17)
            self.assertTrue(self.B.detect_pollution(before2, self.B.fingerprint_all()))
        finally:
            os.environ.pop(self.B.ENV_WATCH_PATHS, None)
            shutil.rmtree(root, ignore_errors=True)


# --------------------------------------------------------------------- G-1
class _FakeArgs:
    def __init__(self, port=8197, disable_pinned_memory=False):
        self.port = port
        self.disable_pinned_memory = disable_pinned_memory


class _FakeMM:
    def __init__(self, max_pinned=32 * 1024**3, total_pinned=0, ram=64 * 1024**3):
        self.MAX_PINNED_MEMORY = max_pinned
        self.TOTAL_PINNED_MEMORY = total_pinned
        self.ram = ram


def load_memory_policy(root: Path, port=8197, mm_file=None, max_pinned=32 * 1024**3):
    """Import H3_MemoryPolicy with stubbed `comfy` modules (no ComfyUI needed)."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "comfy").mkdir(exist_ok=True)
    real_mm = root / "comfy" / "model_management.py"
    real_mm.write_text("# stub\n", encoding="utf-8")

    comfy = types.ModuleType("comfy")
    comfy.__path__ = [str(root / "comfy")]
    cli = types.ModuleType("comfy.cli_args")
    cli.args = _FakeArgs(port=port)
    mm = types.ModuleType("comfy.model_management")
    mm.__file__ = str(mm_file if mm_file else real_mm)
    for attr in ("MAX_PINNED_MEMORY", "TOTAL_PINNED_MEMORY", "ram"):
        setattr(mm, attr, getattr(_FakeMM(max_pinned=max_pinned), attr))
    sys.modules["comfy"] = comfy
    sys.modules["comfy.cli_args"] = cli
    sys.modules["comfy.model_management"] = mm

    for k in list(sys.modules):
        if k.startswith("H3_MemoryPolicy"):
            del sys.modules[k]
    mod = load_by_path("H3_MemoryPolicy_under_test",
                       PK / "H3_MemoryPolicy.disabled" / "__init__.py")
    return mod, mm


class TestMemoryPolicyGateIsAlive(unittest.TestCase):
    """The old `_expected = Path('<REDACTED_LOCAL_PATH>/D')` made this dead code."""

    def test_missing_config_is_reported_not_silently_skipped(self):
        root = Path(tempfile.mkdtemp(prefix="h3_gate_mp_"))
        os.environ.pop("H3_MEMORY_POLICY_COMFY_ROOT", None)
        try:
            mod, _mm = load_memory_policy(root)
            # The defect was a placeholder used as a *path literal* in code, e.g.
            # `Path(r'<REDACTED_LOCAL_PATH>/D')`. The repair note still quotes the
            # old line in prose, so match on the AST, not on raw text.
            src = (PK / "H3_MemoryPolicy.disabled" / "__init__.py").read_text(encoding="utf-8")
            offenders = [n for n in ast.walk(ast.parse(src))
                         if isinstance(n, ast.Constant)
                         and isinstance(n.value, str)
                         and "<REDACTED" in n.value]
            self.assertEqual(offenders, [],
                             "仍然存在把脱敏占位符写进字符串字面量的代码：%s"
                             % [o.value for o in offenders])
            res = mod.self_check(port=8197, mm_file=root / "comfy" / "model_management.py")
            self.assertEqual(res["state"], mod.STATE_CONFIG_MISSING)
            self.assertIn("H3_MEMORY_POLICY_COMFY_ROOT", res["reason"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_wrong_instance_is_skipped_with_a_reason(self):
        root = Path(tempfile.mkdtemp(prefix="h3_gate_mp_"))
        os.environ["H3_MEMORY_POLICY_COMFY_ROOT"] = str(root)
        try:
            mod, _mm = load_memory_policy(root, port=8199)
            res = mod.self_check(port=8199, mm_file=root / "comfy" / "model_management.py")
            self.assertEqual(res["state"], mod.STATE_SKIPPED)
            self.assertIn("8199", res["reason"])
        finally:
            os.environ.pop("H3_MEMORY_POLICY_COMFY_ROOT", None)
            shutil.rmtree(root, ignore_errors=True)

    def test_matching_instance_applies(self):
        """Positive control: the policy really can fire, and clamps the cap."""
        root = Path(tempfile.mkdtemp(prefix="h3_gate_mp_"))
        os.environ["H3_MEMORY_POLICY_COMFY_ROOT"] = str(root)
        try:
            mod, mm = load_memory_policy(root, port=8197, max_pinned=32 * 1024**3)
            mm.MAX_PINNED_MEMORY = 32 * 1024**3
            res = mod.self_check(port=8197, mm_file=root / "comfy" / "model_management.py")
            self.assertEqual(res["state"], mod.STATE_APPLIED, res)
            mod.apply()
            self.assertEqual(mm.MAX_PINNED_MEMORY, 16 * 1024**3)
        finally:
            os.environ.pop("H3_MEMORY_POLICY_COMFY_ROOT", None)
            shutil.rmtree(root, ignore_errors=True)

    def test_disabled_pinned_memory_is_reported(self):
        root = Path(tempfile.mkdtemp(prefix="h3_gate_mp_"))
        os.environ["H3_MEMORY_POLICY_COMFY_ROOT"] = str(root)
        try:
            mod, mm = load_memory_policy(root, port=8197)
            sys.modules["comfy.cli_args"].args.disable_pinned_memory = True
            res = mod.self_check(port=8197, mm_file=root / "comfy" / "model_management.py")
            self.assertEqual(res["state"], mod.STATE_NOT_APPLIED)
        finally:
            sys.modules["comfy.cli_args"].args.disable_pinned_memory = False
            os.environ.pop("H3_MEMORY_POLICY_COMFY_ROOT", None)
            shutil.rmtree(root, ignore_errors=True)


# ------------------------------------------------------------ D-1 / D-2
class TestMissingDependenciesAreDiagnosable(unittest.TestCase):
    """A missing third-party component must say what to install, not crash."""

    def test_audio_refine_missing_names_the_upstream(self):
        mod = load_by_path("audio_refine_loader",
                           PK / "H3_AudioUpgrade" / "audio_refine_loader.py")
        root = Path(tempfile.mkdtemp(prefix="h3_gate_ar_"))
        os.environ["H3_AUDIO_REFINE_DIR"] = str(root / "does_not_exist")
        try:
            self.assertEqual(mod.status()["state"], "MISSING")
            with self.assertRaises(mod.H3AudioRefineMissing) as ctx:
                mod.load_sampler_class()
            msg = str(ctx.exception)
            for needle in ("Adudeguyman/ComfyUI-H3-AudioRefine", "MIT",
                           "fd5a8dfe", "git clone"):
                self.assertIn(needle, msg, "错误信息缺少 %r" % needle)
            self.assertIsNone(mod.load_sampler_class(strict=False))
        finally:
            os.environ.pop("H3_AUDIO_REFINE_DIR", None)
            shutil.rmtree(root, ignore_errors=True)

    def test_audio_refine_present_resolves(self):
        """Positive control: a planted upstream module is found and imported."""
        mod = load_by_path("audio_refine_loader",
                           PK / "H3_AudioUpgrade" / "audio_refine_loader.py")
        root = Path(tempfile.mkdtemp(prefix="h3_gate_ar_")) / "vendor"
        root.mkdir(parents=True)
        (root / "nodes.py").write_text(
            "class H3AudioRefineSampler:\n    pass\n", encoding="utf-8")
        (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
        os.environ["H3_AUDIO_REFINE_DIR"] = str(root)
        try:
            st = mod.status()
            self.assertEqual(st["state"], "PRESENT")
            self.assertTrue(st["has_license"])
            cls = mod.load_sampler_class()
            self.assertEqual(cls.__name__, "H3AudioRefineSampler")
        finally:
            os.environ.pop("H3_AUDIO_REFINE_DIR", None)
            shutil.rmtree(root.parent, ignore_errors=True)

    def test_official_guide_missing_names_the_install_path(self):
        mod = load_by_path("v28_h3_format", V28 / "v28_h3_format.py")
        os.environ.pop(mod.ENV_SKILL_DIR, None)
        self.assertEqual(mod.official_guide_status()["state"], "MISSING")
        with self.assertRaises(mod.H3OfficialGuideMissing) as ctx:
            mod.audit_prompt("subject_definitions:\nx")
        msg = str(ctx.exception)
        self.assertIn("install_minimax_official_skill.py", msg)
        self.assertIn("H3_MINIMAX_OFFICIAL_SKILL_DIR", msg)

    def test_official_guide_present_parses(self):
        """Positive control: a planted guide resolves the six-section contract."""
        mod = load_by_path("v28_h3_format", V28 / "v28_h3_format.py")
        root = Path(tempfile.mkdtemp(prefix="h3_gate_guide_"))
        skill = root / "skill"
        (skill / "references").mkdir(parents=True)
        # Minimal but structurally faithful stand-in: the six-section table plus
        # the four headings _load_guide() slices between to extract enums.
        lines = ["# guide"]
        lines += ["| `%s` | d |" % s for s in mod.SECTION_CONTRACT]
        lines += ["", "Choose task types according to the request.",
                  "| `reference generation` | d |", "| `video continuation` | d |",
                  "", "## 4. Retention", "### 4.1 Visible",
                  "| `fully_preserved` | d |", "### 4.2 Audio",
                  "| `fully_copy` | d |", "## 5. Next"]
        (skill / "references" / "ref-en.txt").write_text(
            "\n".join(lines), encoding="utf-8")
        os.environ[mod.ENV_SKILL_DIR] = str(skill)
        try:
            self.assertEqual(mod.official_guide_status()["state"], "PRESENT")
            self.assertEqual(tuple(mod.SECTIONS), mod.SECTION_CONTRACT)
            self.assertIn("reference generation", mod.TASK_TYPES)
            self.assertIn("fully_preserved", mod.VISIBLE_MARKERS)
            self.assertIn("fully_copy", mod.AUDIO_MARKERS)
        finally:
            os.environ.pop(mod.ENV_SKILL_DIR, None)
            shutil.rmtree(root, ignore_errors=True)


def main():
    print("H3 中文导演台 · 假门禁修复回归测试")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    print("结果：%d 通过 / %d 失败 / %d 跳过"
          % (res.testsRun - len(res.failures) - len(res.errors) - len(res.skipped),
             len(res.failures) + len(res.errors), len(res.skipped)))
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
