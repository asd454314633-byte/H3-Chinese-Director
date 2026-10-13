# 第三方声明（THIRD_PARTY_NOTICES）

> 本文件在 2026-10-13 依据归属审计的修复结论重写。修正了三处与实测不符的旧表述：
> ①「本仓库不重新分发任何第三方项目源码」——发布工作流内含一段官方 blueprint 的
> 派生子图；②「对第三方节点的源码未做修改」——同一子图存在参数面改动；
> ③ 对 MiniMax 官方 Skill 三份文件与未随包 vendor 组件的署名/许可缺漏。
> 修改点逐条列在 [`RELEASE_CANDIDATE_DIFF.md`](RELEASE_CANDIDATE_DIFF.md) 与
> [`OWNERSHIP_CORRECTIONS.csv`](OWNERSHIP_CORRECTIONS.csv)。

## 0. 一句话总览

| 类别 | 许可 | 是否随本仓库分发 |
|---|---|---|
| 本项目自研部分（节点 / 前端 / 工作流编排 / 脚本 / 文档） | MIT | 是 |
| ComfyUI 引擎 | GPL-3.0 | 否（引用安装） |
| 第三方自定义节点 | 各自许可（见 §3） | 否（引用安装） |
| Comfy-Org 官方 workflow blueprint（SDPose 子图派生源） | **MIT** | **是（作为工作流内的一段子图，已标注来源与修改）** |
| Adudeguyman/ComfyUI-H3-AudioRefine | MIT | 否（外部依赖，运行时按需定位） |
| MiniMax 官方 H3 提示词写作 Skill | **未授权（LICENSE_HOLD）** | **否（已从本仓库排除）** |
| 模型权重 | 各自条款 | 否 |

## 1. ComfyUI（引擎）

- 上游：<https://github.com/Comfy-Org/ComfyUI>
- 许可：GPL-3.0
- 关系：本仓库的工作流、自定义节点与前端**运行在其之上**，本仓库不含其源码副本。

> **许可边界（重要）**：ComfyUI 引擎的 GPL-3.0 **不自动延伸**到独立发布的其它仓库。
> 本仓库引用的官方工作流模板仓库 `Comfy-Org/workflow_templates` 是**独立 MIT 仓库**
> （GitHub API `license.spdx_id == "MIT"`，2026-10-13 核实），不因「ComfyUI 是 GPL」
> 而变成 GPL。同理，对 ComfyUI 运行时做调用或覆写（本仓库 8 个模块的情形）
> 与复制/派生其受版权保护的源码是两件事，不能仅凭 monkey-patch 认定违反 GPL；
> 详见 [`docs/UPSTREAM_ATTRIBUTION.md`](docs/UPSTREAM_ATTRIBUTION.md) §2（表格后的「许可边界」说明）
> 与 [`AUTHOR_CONTRIBUTIONS.md`](AUTHOR_CONTRIBUTIONS.md) §14。

## 2. MiniMax-H3 模型 / 官方权重

- 上游模型库：<https://huggingface.co/Comfy-Org/MiniMax-H3>
- 关系：本仓库**不含权重**，`docs/MODELS.md` 给出下载链接、文件名、安装目录与核验方式。
- 注意：模型可能带有授权、地域与商业使用限制，以模型发布方的条款为准。

## 2b. MiniMax 官方 H3 提示词写作 Skill —— **LICENSE_HOLD（不随包）**

本仓库曾包含三份 MiniMax 官方原版文件（已确认去横幅后与上游逐字节相等）：

| 上游仓库 | 上游路径 | 上游 blob SHA1 |
|---|---|---|
| MiniMax-AI/MiniMax-H3 | `skills/h3-prompt-writing/SKILL.md` | `b6d9b2839384a588763a9c24315225dd8ce19d56` |
| MiniMax-AI/MiniMax-H3 | `skills/h3-prompt-writing/references/base-en.txt` | `40cf586a634d677d6b7107b367cf0ec9621be728` |
| MiniMax-AI/MiniMax-H3 | `skills/h3-prompt-writing/references/ref-en.txt` | `7ae1b2d07d743fd2392258a96449be9e9e322d35` |

- 许可状态：上游仓库 `license == null`，无 `LICENSE` / `LICENSE.md` / `LICENSE.txt`；
  Hugging Face 模型卡附一份 Community License Agreement（要求逐字附 NOTICE、
  禁止附加不同条款、含地域限制）。**本仓库未取得再分发授权 ⇒ LICENSE_HOLD。**
- 处置：三份文件已从公开包**排除**，改为指针引用
  （`custom_nodes/.../H3_V28_Director/skills/official-minimax-h3-prompt/README.md`）。
  本仓库**不**对它们声明 MIT —— 此前对整个 authored surface 统一声明 MIT 属于越权授权。
- 若你已自行取得授权：`python scripts/setup/install_minimax_official_skill.py --source <本地副本>`，
  或设置 `H3_MINIMAX_OFFICIAL_SKILL_DIR`。脚本默认不联网下载。

## 2c. Adudeguyman / ComfyUI-H3-AudioRefine —— 外部依赖（不随包）

- 上游：<https://github.com/Adudeguyman/ComfyUI-H3-AudioRefine>
- 作者：Adudeguyman　许可：**MIT**（GitHub API 核实 2026-10-13）
- 钉住版本：commit `fd5a8dfe8b4c636b1877abd07d11ebc985eddbed`（2026-09-06T22:47:23Z），
  `nodes.py` blob `4b8e966f330cb96dfab75b9aeab5ae952c236972`
- 关系：`H3_AudioUpgrade/nodes.py` 在其上做**自研包装层**（自己实现节点、前端开关与
  缓存语义），精修算法本身是该第三方组件提供，本仓库**不分发其源码**。
- 安装：`python scripts/setup/install_h3_audio_refine.py --source <克隆目录>`，
  或设置 `H3_AUDIO_REFINE_DIR`。缺失时节点抛 `H3AudioRefineMissing`
  （含上游地址、许可、钉住版本与安装命令），**不会**退化成裸 `ModuleNotFoundError`，
  也**不会**静默跳过音频精修。

## 3. 第三方 ComfyUI 自定义节点

| 目录名 | 上游仓库 | 作者 | 许可 | 本仓库关系 |
|---|---|---|---|---|
| ComfyUI-KJNodes | <https://github.com/kijai/ComfyUI-KJNodes> | kijai | **GPL-3.0**（经 GitHub API 核实 2026-10-12） | 引用安装 |
| rgthree-comfy | <https://github.com/rgthree/rgthree-comfy> | rgthree | MIT | 引用安装 |
| ComfyUI-MAINodes | <https://github.com/matlowai/ComfyUI-MAINodes> | matlowai | 自定义（SPDX NOASSERTION，以仓库 LICENSE 文本为准） | 引用安装 |
| ComfyUI-Ref2VA-VSA | <https://github.com/Kablex/ComfyUI-Ref2VA-VSA> | Kablex | 自定义（SPDX NOASSERTION，以仓库 LICENSE 文本为准） | 引用安装 |
| ComfyUI-MiniMax-H3-PDD-Acc | <https://github.com/Jalen-Brunson/ComfyUI-MiniMax-H3-PDD-Acc> | Jalen-Brunson | Apache-2.0 | 引用安装 |
| ComfyUI-H3-Motion-Context | <https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context> | NikoDemon80 | (按上游仓库声明) | 引用安装 |
| H3-Optimizations | <https://github.com/Zironic/H3-Optimizations> | Zironic | **分目录确认**：`native/` 子树为 Apache-2.0（版权方 **Comfy Org**，vendored 自 ComfyUI 上游）；仓库其余部分（自研节点）**根目录无 LICENSE**，按版权保留处理 —— 引用安装不分发 | 引用安装 |
| comfyui-obvpm | 上游已改名，见 `docs/UPSTREAM_ATTRIBUTION.md` | obvpm | (按上游仓库声明) | 引用安装 |
| anthropic-claude | <https://github.com/alexmunteanu/comfyui-anthropic-claude> | alexmunteanu | MIT © 2026 Alex Munteanu | 引用安装 |
| comfyui_claude_prompt_generator | <https://github.com/PauldeLavallaz/comfyui_claude_prompt_generator> | PauldeLavallaz | MIT © 2024 Paul de Lavallaz | 引用安装 |
| comfyui-krea2edit | <https://github.com/lbouaraba/comfyui-krea2edit> | conradlocke / lbouaraba | Apache-2.0（pyproject 声明） | 8207 线引用 |
| krea-reference | <https://github.com/kgilper/krea-reference> | kgilper | MIT © 2026 Kevin Gilper | 8207 线引用 |

> 许可核实方式：GitHub API `repos/<owner>/<repo>/license`。SPDX 为 NOASSERTION 或
> 上游无 LICENSE 的项，以各自仓库的文本为准；本仓库未搬运其源码。
>
> **GPL-3.0 特别说明（ComfyUI-KJNodes）**：本仓库不分发 KJNodes 源码、仅引用安装，
> 因此不因本仓库的发布行为触发 GPL 分发义务；但若你修改 KJNodes 源码并对外分发，须遵循 GPL-3.0。

## 4. SDPose 多人姿态子图 —— 官方 blueprint 的派生子图（**本仓库内确有第三方派生内容**）

发布工作流 `workflows/current/V29_chinese_director_production_8197.json` 内的子图
`SDPose Video Pose Extractor [Multi‑Person]` **派生自官方 blueprint**：

| 项 | 值 |
|---|---|
| 官方作者 / 仓库 | Comfy-Org &lt;<https://github.com/Comfy-Org/workflow_templates>&gt; |
| 官方文件 | `blueprints/video_to_pose_map_sdpose_multi_person.json` |
| 官方许可 | **MIT**（仓库根目录 LICENSE，GitHub API 核实 2026-10-13） |
| 钉住提交 | `cdccb2ee7a7cd0baee4630cf7186283a98ab408f`（main，2026-10-12T13:52:16Z） |
| 钉住 blob | `6f6d7ab146a5b143f70bc98d444a7a64829a94ea`（33,268 B） |
| 钉住 SHA256 | `92e31fb99f4a005a9263c296429c99eb0847567d64b1f3a35fa42839e0cbfec2` |
| 复核脚本 | `python scripts/verify/verify_sdpose_blueprint.py` |

**相同的部分（对外契约逐字段全等）**：子图 `inputs` 15/15、`outputs` 5/5
（规范化 SHA 分别为 `1d774f0ce564bf66`、`bbe3df7daa6ceddc`，两侧一致）；
节点数 7/7、连线数 28/28、节点类型集合一致
（`CheckpointLoaderSimple` / `GetVideoComponents` / `RTDETR_detect` /
`ResizeImageMaskNode` / `SDPoseDrawKeypoints` / `SDPoseKeypointExtractor` / `UNETLoader`）。

**本项目所做的修改（80 处节点叶子字段 + 10 处连线叶子字段，由上述脚本复算）**，主要包括：

- 子图 `id` 改写（`01b6a731-…` → `622cceeb-…`）、`name` 改为中文界面下的
  `SDPose Video Pose Extractor [Multi‑Person]`、`category` 由 `Preprocessors/Pose` 置为 `null`；
- 12 处 `localized_name` 改为中文；
- 7 处仅发布副本才有的 `widgets_values_named` 键；
- 删除 `batch_size` / `resize_type` / `weight_dtype` 三个可选输入槽；
- 5 处执行 `order`、2 处节点 id 重编号（673→1065、674→1064）、2 处画布 `size`；
- 1 处输出类型 `*` → `IMAGE`；`SDPoseDrawKeypoints` 多出第 8 个控件值 `true`；
- 8/28 条连线因端点重编号与槽位顺移而不同；
- 子图 `state` 计数器被改写。

**判读**：该子图是官方 MIT blueprint 的**派生子图**，不是「完全原创」，也不是
「未做修改」。其权重（`sdpose_wholebody_fp16.safetensors`、
`rt_detr_v4-x-hgnet_fp16.safetensors`）来自
<https://huggingface.co/Comfy-Org/SDPose>，不含在本仓库。

**钉住副本（本仓库内唯一的第三方逐字节副本）**：`docs/evidence/sdpose_blueprint_pinned.json`
是上述官方 blob 的**逐字节副本**（33,268 B，SHA256 与钉住值一致），随本仓库分发，
用途是让 `verify_sdpose_blueprint.py` 能**离线**复核。该文件为 **MIT 许可的上游作品**，
来源、许可与逐项修改声明见 `docs/evidence/README.md` —— 本仓库**不**对其主张原创、也**不**
对其授 MIT（其许可来自上游 Comfy-Org 的 MIT）。若你不希望随包带走该副本，删除它不会影响
生产运行，只会让离线复核脚本改走联网模式。

## 5. 来源不明 / 证据不足的项目（已排除源码）

- `MiniMax-H3-Combined-Image-And-Reference-to-Video`：本机存在、带 GPL-3.0 文本，但
  **无上游仓库地址与作者信息**，溯源证据不足 → 本仓库**不发布其源码**，仅登记为
  「第三方，来源待核」。若你是作者或知情者，请通过 issue 联系。

## 6. 修改声明（已按实测修正）

- 对**第三方节点包**的源码：本仓库未做修改（未 fork、未 patch），仅引用安装。
- 对**官方 blueprint**：存在派生修改，见 §4（旧版本文件称「未做修改」与实测不符，已更正）。
- 对 **ComfyUI 运行时**：本仓库有 8 个模块通过 monkey-patch / 覆写改变上游运行行为
  （生命周期与显存管理），属「调用或覆写上游运行时」，非「复制或派生上游源码」；
  这些模块与 ComfyUI 版本强耦合，升级上游需重新验证，见
  [`AUTHOR_CONTRIBUTIONS.md`](AUTHOR_CONTRIBUTIONS.md) §14。
- 本地作者的其它改动集中在：原创节点、原创前端、原创工作流编排。

## 7. 未决项（HOLD）

尚未取得结论、本轮**不做法律定论**的事项：

1. MiniMax 官方 Skill 三份文件的再分发授权（§2b）—— 等待书面授权或改为纯引用。
2. 衍生作品法律关系（monkey-patch 是否构成 ComfyUI GPL 下的衍生作品）——
   本仓库只陈述事实（调用/覆写 vs 复制源码），不作结论。
3. 上游无 LICENSE 或 SPDX NOASSERTION 的若干节点包（§3）—— 以各自仓库文本为准。

完整清单见 [`REMAINING_HOLD.md`](REMAINING_HOLD.md)。
