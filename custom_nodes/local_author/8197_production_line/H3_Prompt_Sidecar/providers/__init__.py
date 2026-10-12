# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import configparser
import importlib
from pathlib import Path
from .base import ModelRequest, ModelResponse, ModelProvider, ProviderError

def create_provider(config_path: Path) -> ModelProvider:
    config = configparser.ConfigParser(interpolation=None)
    if not config.read(config_path, encoding="utf-8"):
        raise ProviderError(f"SIDECAR_CONFIG_MISSING: {config_path}")
    if config.has_section('director'):
        from .registry import RegisteredProvider
        return RegisteredProvider(config_path)
    name = config["sidecar"]["model_provider"]
    # Only local_llamacpp is shipped. Future modules export create(config).
    if not name.isidentifier():
        raise ProviderError("SIDECAR_PROVIDER_INVALID")
    module = importlib.import_module(f"{__name__}.{name}")
    section = config[name]
    if name == "local_llamacpp":
        return module.LocalLlamaCppProvider(section)
    return module.create(section)
