# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import json
from pathlib import Path
from . import cache_codec
cache_codec.MODEL_REGISTRY={str(Path(r['path']).resolve()):r for r in json.loads(Path(__file__).with_name('model_registry.json').read_text())}
from .nodes import NODE_CLASS_MAPPINGS
WEB_DIRECTORY = './web'
from .production import register
register()
if Path(__file__).with_name('observe.enabled').exists():
 from . import observer
