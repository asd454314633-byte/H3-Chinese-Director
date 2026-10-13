# -*- coding: utf-8 -*-
"""8207 隔离验证线的路径配置（由脱敏占位符改为显式配置）。

背景：这些脚本的私有原件把 8207 隔离环境的根目录与 Python 解释器路径写成
真实本机绝对路径；内容级脱敏时整个字符串常量被替换为 `<REDACTED_LOCAL_PATH>/D`，
导致脚本拿到一个永不存在的目录 —— 既不会报"配置缺失"，也会在 rglob/copy 时
产生误导性结果（空结果被当成"没有差异"）。

修复方式与 G-1 / G-3 一致：**环境变量显式配置 + 未配置时明确失败**，
不恢复任何真实私有路径，也不在缺失时静默降级。

用法：
    set H3_8207_TASK_ROOT=D:\\你的\\8207\\隔离目录
    set H3_8207_PYTHON=D:\\你的\\8207\\隔离目录\\runtime\\.venv\\Scripts\\python.exe
"""

import os
import pathlib

ENV_TASK_ROOT = "H3_8207_TASK_ROOT"
ENV_PYTHON = "H3_8207_PYTHON"


class H3_8207ConfigError(RuntimeError):
    """Raised when the 8207 isolation-line paths are not configured."""


def _require(name, what):
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        raise H3_8207ConfigError(
            "8207 隔离线路径未配置：请设置环境变量 %s 指向你的 8207 隔离环境根目录。\n"
            "  这是脱敏后的公开副本，私有原件里的真实本机路径**不会**被恢复、也不会被猜测。\n"
            "  示例（Windows）：set %s=D:\\你的\\8207\\隔离目录\n"
            "  用途：%s" % (name, name, what)
        )
    p = pathlib.Path(raw)
    if not p.exists():
        raise H3_8207ConfigError(
            "环境变量 %s 指向的目录不存在：%s\n"
            "  请指向一个真实的、可写的 8207 隔离环境根目录。" % (name, p)
        )
    return p


def task_root():
    """8207 隔离环境根目录（含 runtime/、logs/、baseline/ 等）。"""
    return _require(ENV_TASK_ROOT, "8207 隔离环境根目录（其下有 runtime/、logs/）")


def _require_file(name, what):
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        raise H3_8207ConfigError(
            "缺少 8207 线的输入文件配置：请设置环境变量 %s。\n"
            "  用途：%s\n"
            "  私有原件里的绝对路径已被脱敏移除，这里不做任何猜测，也不静默跳过。" % (name, what)
        )
    p = pathlib.Path(raw)
    if not p.is_file():
        raise H3_8207ConfigError("环境变量 %s 指向的文件不存在：%s" % (name, p))
    return p


def production_workflow():
    """8197 冻结生产工作流原件（脚本会校验其 SHA256 后再作为基线）。"""
    return _require_file("H3_8207_PRODUCTION_WORKFLOW",
                         "8197 冻结生产工作流 JSON，用作 8207 镜像的基线（会先校验 SHA256）")


def ui_freeze_json():
    """UI 冻结清单 JSON（含 runtime_source_hashes，用于漂移比对）。"""
    return _require_file("H3_8207_UI_FREEZE_JSON",
                         "UI 冻结清单 JSON（含 runtime_source_hashes）")


def python_exe():
    """8207 隔离环境使用的 Python 解释器可执行文件。"""
    raw = (os.environ.get(ENV_PYTHON) or "").strip()
    if not raw:
        raise H3_8207ConfigError(
            "8207 隔离线的 Python 解释器未配置：请设置环境变量 %s 指向 python.exe。\n"
            "  示例：set %s=D:\\你的\\8207\\隔离目录\\.venv\\Scripts\\python.exe\n"
            "  说明：私有原件里的解释器绝对路径已被脱敏移除，这里不做任何猜测。"
            % (ENV_PYTHON, ENV_PYTHON)
        )
    p = pathlib.Path(raw)
    if not p.exists():
        raise H3_8207ConfigError("环境变量 %s 指向的解释器不存在：%s" % (ENV_PYTHON, p))
    return p
