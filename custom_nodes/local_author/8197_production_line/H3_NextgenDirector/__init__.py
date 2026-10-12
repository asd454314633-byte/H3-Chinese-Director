# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
from comfy_api.latest import ComfyExtension, io
from .nodes import H3GuideTimeline

WEB_DIRECTORY = "./js"

class H3NextgenDirectorExtension(ComfyExtension):
    async def get_node_list(self):
        return [H3GuideTimeline]

async def comfy_entrypoint():
    return H3NextgenDirectorExtension()

__all__ = ["WEB_DIRECTORY"]