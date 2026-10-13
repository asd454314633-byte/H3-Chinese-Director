# 上游依赖归属与安装（UPSTREAM_ATTRIBUTION）

本文件枚举本项目**实际依赖**的第三方自定义节点、前端扩展与 Python 包，并给出作者、仓库 URL、版本/锁定方式、许可、安装方法与「是否被本地作者修改」。
原则：**原版第三方项目以安装链接与版本锁定为主，不搬运源码。**

## 1. ComfyUI 引擎

| 项 | 值 |
|---|---|
| 上游 | <https://github.com/Comfy-Org/ComfyUI> |
| 许可 | GPL-3.0 |
| 本仓库关系 | 运行宿主；本仓库不含其源码 |
| 版本指纹（8197 冻结线） | 工作流 `extra.h3_v281_production.core = "0.36.0"`；前端 `extra.frontendVersion = "1.52.7"` |

前端版本锁定说明：`COMFYUI_FRONTEND_VERSION_LOCK = 1.52.7`。1.53.6 存在「tab 切换恢复 `mode=0`」的已知回归，升级前必须加门禁。

## 2. 第三方自定义节点

安装方式统一为：进入 `ComfyUI/custom_nodes/`，`git clone <url>`（或用 ComfyUI Manager 按 URL 安装），然后重启 ComfyUI。

| 节点包 | 上游仓库 | 作者 | 许可 | 是否被本地作者修改 |
|---|---|---|---|---|
| ComfyUI-KJNodes | <https://github.com/kijai/ComfyUI-KJNodes> | kijai | **GPL-3.0**（上游 LICENSE，经 GitHub API 核实 2026-10-12；v1.0 误标 MIT 已修正） | 否 |
| rgthree-comfy | <https://github.com/rgthree/rgthree-comfy> | rgthree | MIT（经 GitHub API 核实 2026-10-12） | 否 |
| ComfyUI-MAINodes | <https://github.com/matlowai/ComfyUI-MAINodes> | matlowai | 自定义 LICENSE（GitHub API SPDX 探测为 NOASSERTION），以仓库内 LICENSE 文本为准 | 否 |
| ComfyUI-Ref2VA-VSA | <https://github.com/Kablex/ComfyUI-Ref2VA-VSA> | Kablex | 自定义 LICENSE（本地记录为 Apache-2.0 文本；GitHub API SPDX 探测为 NOASSERTION），以仓库内 LICENSE 文本为准 | 否 |
| ComfyUI-MiniMax-H3-PDD-Acc | <https://github.com/Jalen-Brunson/ComfyUI-MiniMax-H3-PDD-Acc> | Jalen-Brunson | Apache-2.0（经 GitHub API 核实 2026-10-12） | 否（本地作者仅在其机制之上做生命周期二次开发，见下） |
| ComfyUI-H3-Motion-Context | <https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context> | NikoDemon80 | 见上游 LICENSE | 否 |
| H3-Optimizations | <https://github.com/Zironic/H3-Optimizations> | Zironic | **分目录确认**（2026-10-13 复核）：`native/LICENSE` 为 Apache-2.0，版权声明 "Copyright (c) 2025 Comfy Org"（vendored 自 ComfyUI 上游的 native 组件，**不能代表整包**）；仓库其余部分根目录无 LICENSE，按版权保留处理，不做无依据法律定论 | 否 |
| comfyui-obvpm | <https://github.com/obvpm/comfyui-obvpm> | obvpm | 见上游 LICENSE | 否 |
| anthropic-claude | <https://github.com/alexmunteanu/comfyui-anthropic-claude> | alexmunteanu | 见上游 LICENSE | 否（仅提示词辅助，非生产必需） |
| comfyui_claude_prompt_generator | <https://github.com/PauldeLavallaz/comfyui_claude_prompt_generator> | PauldeLavallaz | 见上游 LICENSE | 否（非生产必需） |
| **ComfyUI-H3-AudioRefine（外部依赖，不随包）** | <https://github.com/Adudeguyman/ComfyUI-H3-AudioRefine> | **Adudeguyman** | **MIT** © 2026 Adudeguyman（经 GitHub API 核实 2026-10-13） | 否（本仓库只提供包装层 `H3_AudioUpgrade`，上游采样器以外部依赖形式安装） |

> **GPL-3.0 说明（ComfyUI-KJNodes 与 ComfyUI 宿主）**：两者均为 GPL-3.0。本仓库**不分发**它们的源码，仅以"引用安装"方式使用，不触发 GPL 分发义务；若您修改其源码并对外分发，须遵循 GPL-3.0。
>
> **GPL 不自动延伸**：ComfyUI 宿主是 GPL-3.0，但这**不**意味着所有与 ComfyUI 相关的仓库都被 GPL 覆盖。
> 例如本仓库派生的 SDPose 蓝图来自独立仓库 `Comfy-Org/workflow_templates`（根 LICENSE = **MIT**），
> 该仓库的许可以其自身 LICENSE 为准。判定许可时**按每个仓库自己的 LICENSE 文件**，不按宿主推导。

> **obvpm 名称说明**：`comfyui-obvpm` 的仓库名/作者名在上游可能发生过改名。本表以**仓库 URL 与仓库内 LICENSE 文本**为归属依据，不以目录名为依据；若 URL 不可达，请以实际可达的仓库为准并回报。

### 8207 线额外引用（不在公开包内，仅登记归属）

以下节点为 8207 实验线专用，**不随本公开包分发、也无需安装**；登记在此仅为归属与许可可追溯：

| 节点包 | 说明 | 许可 |
|---|---|---|
| comfyui-krea2edit（ComfyUI-Krea2Edit） | Krea 2 指令式图像编辑，8207 线实验 | Apache-2.0 |
| krea-reference | <https://github.com/kgilper/krea-reference> | 见上游 LICENSE |

### 来源不明（已排除，不发布源码）

- `MiniMax-H3-Combined-Image-And-Reference-to-Video`：本机存在且带 GPL-3.0 文本，但无上游仓库地址与作者信息，溯源证据不足 → **不搬运源码**，仅登记为「第三方，来源待核」。许可标记为 `LICENSE_HOLD`（本机仅残留 LICENSE 文本，未经权威源核实）。

## 2b. MiniMax 官方 H3 提示词 Skill（第三方原版，已移除，改为外部依赖）

| 项 | 值 |
|---|---|
| 上游仓库 | <https://github.com/MiniMax-AI/MiniMax-H3>，路径 `skills/h3-prompt-writing/` |
| 涉及文件 | `SKILL.md`、`references/base-en.txt`、`references/ref-en.txt` |
| 判定 | 与上游同名文件 blob（LF 归一化后）**逐字节相等** → 官方原版，**不是本项目自撰** |
| 许可 | **`LICENSE_HOLD`**：GitHub API `license == null`；模型/Skill 走 Hugging Face *MiniMax Community License Agreement*（含地域与商业限制） |
| 处理 | 已从公开包 `git rm`；`skills/official-minimax-h3-prompt/README.md` 保留来源、版本、blob SHA、比对证据 |
| 运行时 | `v28_h3_format` 确实在运行时解析 `references/ref-en.txt`（六段标题/`TASK_TYPES`/`VISIBLE_MARKERS`/`AUDIO_MARKERS`）。用 `python scripts/setup/install_minimax_official_skill.py --source <副本>` 安装，或设 `H3_MINIMAX_OFFICIAL_SKILL_DIR`；缺失抛 `H3OfficialGuideMissing` |

**未做**：未在未取得授权前自动下载、捆绑或重分发这三份官方原版文件。

## 2c. SDPose 多人姿态蓝图（官方模板仓库，MIT —— 派生件）

| 项 | 值 |
|---|---|
| 上游仓库 | <https://github.com/Comfy-Org/workflow_templates>（仓库根 LICENSE = **MIT**） |
| 提交 | `cdccb2ee7a7cd0baee4630cf7186283a98ab408f` |
| 蓝图路径 | `blueprints/video_to_pose_map_sdpose_multi_person.json` |
| Blob / 大小 / SHA256 | `6f6d7ab146a5b143f70bc98d444a7a64829a94ea` / `33268` / `92e31fb99f4a005a9263c296429c99eb0847567d64b1f3a35fa42839e0cbfec2` |
| 在本仓库的位置 | 唯一工作流 `definitions.subgraphs[1]` |
| 归属类型 | **E —— 派生件，不是完全原创** |
| 全等部分 | inputs 15/15、outputs 5/5、节点 7/7、连线 28/28 |
| 本项目修改 | 80 处节点叶子 + 10 处连线叶子（含 id/name 改写） |
| 复核脚本 | `python scripts/verify/verify_sdpose_blueprint.py`（打印 `SDPOSE_BLUEPRINT=PASS`） |
| 钉住副本 | `docs/evidence/sdpose_blueprint_pinned.json` |

官方文件是 workflow wrapper（顶层 1 个占位节点），蓝图本体在 `definitions.subgraphs[0]` —— 直接比对顶层会把结果误判为 FAIL。

## 2d. ComfyUI 内置节点（引用其运行时与节点类型名）

本仓库的工作流与 8 个自研模块引用 ComfyUI 内置 / `comfy_extras` 节点，**不搬运其源码**：

- 工作流内节点类型：`PreviewImage`、`LTXVSeparateAVLatent`、`LTXVConcatAVLatent`、`H3SixDirectorState` 等
- 自研模块 import / 覆写的符号：`comfy_extras.nodes_minimax_h3.MiniMaxH3ReferenceToVideo`、`MiniMaxH3AddGuide`、`_resize`、`CANVAS_MULTIPLE`；`comfy_extras.nodes_custom_sampler.BasicScheduler`；`comfy_extras.nodes_audio.LoadAudio`；`comfy_extras.nodes_resolution.ResolutionSelector`；`comfy_extras.nodes_math.MathExpressionNode`

这些属于**运行时耦合 / 版本依赖**，不构成对其源码的复制或派生；逐项耦合对象与失效表现见 `AUTHOR_CONTRIBUTIONS.md` §14。

## 3. 与本地作者代码的依赖关系

- `h3_adaptive_host_warm_inplace`（本地作者自研）**依赖** PDD-Acc 的 patch/clone 机制，并做了兼容处理：不再以 PDD clone 的 308 个 patch 作为放行前提，支持官方 `LoadedModel` 回退父 patcher。这是**二次开发**（类型 B），不是对上游源码的 fork。
- `h3_conditioning_prebake`（本地作者自研）依赖 ComfyUI 的 conditioning / 模型加载机制，但缓存键设计、失效语义与回执校验均为原创。
- 工作流中的 `H3*Selector` 节点（本地作者自研）产出的是 Core / 第三方节点能直接消费的原生枚举值，属于**编排层**（类型 C）。

## 4. Python 包

最小集（以你的 ComfyUI 环境为准，本仓库不锁定 venv）：

- `torch` / `torchvision` / `torchaudio`（与你的 CUDA 版本匹配）
- `numpy`、`pillow`、`safetensors`、`transformers`（随 ComfyUI 依赖）
- `ffmpeg`（合并与音频链路，需可执行文件在系统 PATH）

加速库（可选，按第三方节点说明安装）：
- `sage-attention`（Sage Attention 档位）
- `triton`（部分 VSA / BlockSparse 实现需要）
- `xformers`（可选）

## 5. 版本锁定建议

- 本仓库**不提供**第三方节点的 commit 级锁定文件（不搬运其源码，无法校验其哈希）。
- 建议在部署时自行记录 `git -C custom_nodes/<pkg> rev-parse HEAD` 并写入你的部署清单，便于复现与回滚。
- 已知需要门禁的版本：ComfyUI 前端 1.53.6（tab 切换恢复 `mode=0` 回归）→ 保持在 1.52.7 或自行加回归测试后再升级。
