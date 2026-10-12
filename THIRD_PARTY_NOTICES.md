# 第三方声明（THIRD_PARTY_NOTICES）

本仓库**不重新分发**任何第三方项目源码（除本地作者依法可发布的原创部分）。以下项目以「安装引用 + 版本锁定」的方式被依赖，其版权与许可归各自作者所有。

## 1. ComfyUI（引擎）

- 上游：<https://github.com/Comfy-Org/ComfyUI>
- 许可：GPL-3.0
- 关系：本仓库的工作流、自定义节点与前端**运行在其之上**，本仓库不含其源码副本。

## 2. MiniMax-H3 模型 / 官方权重

- 上游模型库：<https://huggingface.co/Comfy-Org/MiniMax-H3>
- 关系：本仓库**不含权重**，`docs/MODELS.md` 给出下载链接、文件名、安装目录与核验方式。
- 注意：模型可能带有授权、地域与商业使用限制，以模型发布方的条款为准。

## 3. 第三方 ComfyUI 自定义节点

| 目录名 | 上游仓库 | 作者 | 许可 | 本仓库关系 |
|---|---|---|---|---|
| ComfyUI-KJNodes | <https://github.com/kijai/ComfyUI-KJNodes> | kijai | **GPL-3.0**（上游 LICENSE，经 GitHub API 核实 2026-10-12） | 引用安装（本仓库不分发其源码） |
| rgthree-comfy | <https://github.com/rgthree/rgthree-comfy> | rgthree | MIT（经 GitHub API 核实 2026-10-12） | 引用安装 |
| ComfyUI-MAINodes | <https://github.com/matlowai/ComfyUI-MAINodes> | matlowai | 自定义 LICENSE（GitHub API SPDX 探测为 NOASSERTION），以仓库内 LICENSE 文本为准 | 引用安装 |
| ComfyUI-Ref2VA-VSA | <https://github.com/Kablex/ComfyUI-Ref2VA-VSA> | Kablex | 自定义 LICENSE（本地记录为 Apache-2.0 文本；GitHub API SPDX 探测为 NOASSERTION），以仓库内 LICENSE 文本为准 | 引用安装 |
| ComfyUI-MiniMax-H3-PDD-Acc | <https://github.com/Jalen-Brunson/ComfyUI-MiniMax-H3-PDD-Acc> | Jalen-Brunson | Apache-2.0（经 GitHub API 核实 2026-10-12） | 引用安装（本地作者未修改其源码） |
| ComfyUI-H3-Motion-Context | <https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context> | NikoDemon80 | (按上游仓库声明) | 引用安装 |
| H3-Optimizations | <https://github.com/Zironic/H3-Optimizations> | Zironic | (按上游仓库声明) | 引用安装 |
| comfyui-obvpm | <https://github.com/obvpm/comfyui-obvpm> | obvpm | (按上游仓库声明) | 引用安装 |
| anthropic-claude | <https://github.com/alexmunteanu/comfyui-anthropic-claude> | alexmunteanu | (按上游仓库声明) | 引用安装 |
| comfyui_claude_prompt_generator | <https://github.com/PauldeLavallaz/comfyui_claude_prompt_generator> | PauldeLavallaz | (按上游仓库声明) | 引用安装 |
| comfyui-krea2edit (ComfyUI-Krea2Edit) | 上游 Krea 2 编辑节点包 | conradlocke | Apache-2.0 | 8207 线引用 |
| krea-reference | <https://github.com/kgilper/krea-reference> | kgilper | (按上游仓库声明) | 8207 线引用 |

> 上述「自定义 LICENSE / 按上游仓库声明」的许可项：本仓库未搬运其源码，安装时请以各自仓库的 `LICENSE` 为准。若某项许可在上游不可确认，请**不要**在闭源/商业场景中直接依赖，并自行核证。
>
> **GPL-3.0 特别说明（ComfyUI-KJNodes）**：其上游许可为 **GPL-3.0**（v1.0 误标为 MIT，已于 2026-10-12 修正）。本仓库**不分发** KJNodes 源码、仅以"引用安装"方式使用，因此不触发 GPL 的分发义务；但若您修改 KJNodes 源码并对外分发，须遵循 GPL-3.0。
>
> 许可核实方式：GitHub API `repos/<owner>/<repo>/license`（2026-10-12 核实）；SPDX 为 NOASSERTION 的项以仓库内 LICENSE 文本原文为准。

## 4. SDPose 多人姿态子图

- 工作流子图 `SDPose Video Pose Extractor [Multi‑Person]` 使用的权重来自
  <https://huggingface.co/Comfy-Org/SDPose>（`sdpose_wholebody_fp16.safetensors`、`rt_detr_v4-x-hgnet_fp16.safetensors`）
- 子图结构为社区既有结构，本仓库保留其接线并标注来源；权重不含在本仓库。

## 5. 来源不明 / 证据不足的项目（已排除源码）

- `MiniMax-H3-Combined-Image-And-Reference-to-Video`：本机存在、带 GPL-3.0 文本，但**无上游仓库地址与作者信息**，溯源证据不足。按「证据不足即排除」原则，本仓库**不发布其源码**，仅在节点清单中登记为「第三方，来源待核」。
- 若你是该项目的作者或知情者，请通过 issue 联系，本仓库将补充准确署名与许可。

## 6. 修改声明

- 本仓库对第三方节点的**源码未做修改**（未 fork、未 patch）。
- 本地作者的改动集中在：原创节点、原创前端、原创工作流编排，以及**基于上游加载/卸载机制**的生命周期二次开发（见 `AUTHOR_CONTRIBUTIONS.md` 第 8 项，属二次开发且已说明差异）。
