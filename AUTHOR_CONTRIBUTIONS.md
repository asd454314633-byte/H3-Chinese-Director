# 本地作者原创贡献清单（AUTHOR_CONTRIBUTIONS）

本文逐项给出：**用途 → 设计特点 → 确切源码路径 → 与上游项目的代码差异 → 首次/当前版本 → 关联测试与验收记录 → 归属类型 → 核实状态**。

归属类型定义（**本仓库与 `manifests/nodes.csv`、`THIRD_PARTY_NOTICES.md` 使用同一套字母含义**）：

| 代码 | 含义 | 判定要点 |
|---|---|---|
| `A` | 本地作者独立设计与自研实现 | 无上游源码来源；不复制、不派生任何第三方受版权保护源码 |
| `B` | 在第三方代码/运行时基础上的二次开发 | 包装层与集成逻辑自研；**上游组件以外部依赖形式安装、不随包搬运**；已说明差异、上游坐标与许可 |
| `C` | 本地作者原创工作流编排与系统集成 | 下游被编排的节点为第三方/Core；原创性体现在拓扑、时序、状态机与门控 |
| `D` | 直接使用的第三方原版节点/文件 | **不归于本作者原创**；源码不搬运（含"已识别并从公开包移除的官方原版文件"） |
| `E` | 派生自上游公开蓝图/官方模板的派生件 | **不宣称完全原创**；已钉住上游 commit/blob、已列明全等部分与逐项修改 |

> **两个必须区分的边界**（不得混为一谈）：
> 1. **调用或覆写上游运行时**（import、monkey-patch、覆写 `execute` 入口、注册 patcher）**不等于**复制或派生上游受版权保护源码。前者只构成运行时耦合与版本依赖，本仓库按 `A`/`B`/`C` 登记并显式标注耦合对象。
> 2. **复制或派生上游源文件/蓝图 JSON** 才构成派生作品，按 `E` 登记并附带上游许可与修改声明。
> 因此，不能仅凭 monkey-patch 就认定违反 GPL-3.0；也不能把 `E` 类派生件写成"完全原创"。

> **旧台账字母含义冲突与本次重映射**（`ORIGIN_AUDIT.csv` 的 `CLASS` 列与本文件的字母**不同义**，已统一）：
>
> | 旧 `CLASS` | 旧规则名 | 旧数量 | 本次处理 |
> |---|---|---|---|
> | `A` | `R_A_ORIGINAL_LINEAGE_*` | 149 | 保留 `A`，但**再分层**（见下方统计口径：122 有版本链 / 27 无版本链） |
> | `B` | `R_B_SELF_AUTHORED_OVER_THIRD_PARTY_EXECUTORS` + `R_B_SELF_COMPOSED_WORKFLOW` | 13 | 保留 `B`；含义收紧为"自研包装层 + 上游组件外部安装" |
> | `C` | `R_C_UPSTREAM_BEHAVIOUR_OVERRIDE` | 8 | 保留 `C`，含义收紧为"覆写上游**运行行为**"，与"工作流编排"分开 |
> | `D` | `R_D_VERBATIM_THIRD_PARTY` | 3 | 保留 `D`（逐字节第三方原版）；本次新增 1 项（SDPose 钉住副本） |
> | `E` | `R_E_ORIGIN_UNCONFIRMED` | 2 | **重映射**：`E` 改用于"上游蓝图/模板的派生件"；旧的 2 个"来源未确认"文件改为**证据状态** `UNCONFIRMED_ORIGIN`，不再占用归属类别字母 |
>
> 旧 `E` 的 2 个文件是 `.gitignore` 与 `fixtures/synthetic/synthetic_ref2va_prompt_template.txt`，
> 它们既不是"派生件"也不是"第三方原版"，放在归属类别里本身就是分类错误。

核实状态：`VERIFIED_BY_SOURCE`（已比对源码）/ `VERIFIED_BY_TEST`（有测试或真实验收）/
`VERIFIED_UPSTREAM_API`（经上游 API 核实仓库与许可）/ `VERIFIED_UPSTREAM_BLOB_EQUAL`（与上游 blob 归一化逐字节相等）/
`VERIFIED_BY_BLOB_DIFF`（与钉住 blob 做了结构化差异复核）/
`DECLARED_RUNTIME_COUPLING`（仅声明运行时耦合，未做源码比对）/
`DECLARED_NOT_FULLY_VERIFIED`（功能存在但未完全验收，明确不谎称 PASS）。

## 0. 统计口径（与 `manifests/nodes.csv` 对齐，2026-10-13 修订）

口径来源：`_audit/ORIGIN_AUDIT.csv`（175 行，2026-10-12 生成的审计基线）。

| 口径 | 数量 | 说明 |
|---|---|---|
| 审计覆盖的文件总数 | 175 | — |
| `manifests/nodes.csv` 条目 | 42 | A 20 / D 15 / C 5 / B 1 / E 1（按**节点包/成果**计数，与下面的**文件**计数不是同一层） |
| 旧台账 `CLASS=A` 的文件 | 149 | 其中 **122 / 27** 需分开看（见下两行） |
| **有本机私有开发版本链**的 A 类文件 | **122** | `DEV_EVIDENCE_TIER`：L0 多版本链 71 + L1 单一前驱 48 + L1R 改名内容前驱 3。**原创性有版本链证据支撑**，不只靠声明 |
| **仅外部语料未发现重复、但原创过程尚未充分证明**的文件 | **27** | `R_A_ORIGINAL_UNIQUE_NO_LINEAGE`（`DEV_EVIDENCE_TIER=L3_NONE`）。判定为"**来源未发现重复，但原创过程尚未充分证明**"，**不**与 122 项混为一谈、也**不**直接宣称已证原创 |
| 修改上游运行行为的自研模块（版本耦合/兼容性/上游依赖） | **8** | `R_C_UPSTREAM_BEHAVIOUR_OVERRIDE`；逐项耦合对象与失效表现见 §14 |
| 自研包装层建于第三方执行体之上（`B`） | 13 | 含 `H3_AudioUpgrade` 等 |
| 逐字节第三方原版（`D`） | 3 + 1 | MiniMax 官方 Skill 三份（已移除）+ 新增 SDPose 钉住副本 `docs/evidence/sdpose_blueprint_pinned.json` |
| 上游蓝图派生件（`E`） | 1 | SDPose 多人姿态子图，见 §16 |
| 本次从公开包移除的第三方官方原版文件 | 3 | MiniMax 官方 Skill 三份（见 §15） |
| 标记为 `LICENSE_HOLD`、未做法律定论的项目 | 见 `REMAINING_HOLD.md` | 未取得授权前不重分发、不自行判定许可 |

---

## 1. 全中文集中控制导演台 【A】

- **用途**：把 V29 工作流 181 个节点收敛为画布上**唯一用户入口**（节点 `N159 H3OperationSelector`，标题「【H3 全中文傻瓜导演台】只需要操作这里」），底层节点仅作为执行引擎。
- **设计特点**：`extra.h3_foolproof_instruction` 固化这一契约；所有选择器（`H3GenerationModeSelector` / `H3ImageModeSelector` / `H3Ref2vaBackendSelector` / `H3Ref2vaAttentionSelector` / `H3SpeedModeSelector` / `H3Fl2vRouteSelector` / `H3SizeModeSelector` / `H3OperationSelector` / `H3GuideModeSelector` / `H3MemoryOptimizationSelector`）以中文选项暴露，底层仍映射到 Core/第三方节点的原生枚举。
- **源码**：`custom_nodes/local_author/8197_production_line/h3_workflow_helpers/`（节点注册与 helper），选项枚举随工作流 `widgets_values` 一并发布在 `workflows/current/V29_chinese_director_production_8197.json`（本仓库唯一公开工作流）。
- **与上游差异**：上游（ComfyUI Core / MiniMax-H3 官方模板）为多节点手工操作，无中文集中语义层；本设计新增「中文语义 → 原生枚举」映射层与单入口门控。
- **版本**：v014 单控制台（`extra.h3_dashboard_version`）→ V28.2 生产 UI → V29 中文开关层（`extra.h3_chinese_switches`）。
- **测试**：浏览器 fresh load 181 节点/218 连线；82 节点 `graphToPrompt` 干跑 required-input errors=0。
- **核实**：`VERIFIED_BY_SOURCE` + `VERIFIED_BY_TEST`。

## 2. 六段剧情编辑与状态管理 【A】

- **用途**：六段中文剧情的编辑、持久化、续跑（resume）与执行态。
- **设计特点**：`H3SixDirectorState`（画布节点 992）持有 `properties.six_prompt_state`：`{texts[6], goal, settings, model, execution:{continuous,start_index,start_mode,project_id}, video_refs[6]}`；`extra.h3_six_segment_director` 描述宿主关系（`prompt_node=138, host_node=992, host_type=H3SixDirectorState`）。
- **源码**：`custom_nodes/local_author/8197_production_line/H3_Prompt_Sidecar/web/h3_six_segment_director.js`、`h3_six_execute.js`、`h3_six_width_contract.js`、`six_resume.py`（8207 线同名文件为独立演进版，未随本仓库发布）。
- **与上游差异**：上游无六段状态机；本实现定义了 6 槽文本 + 每槽参考素材 + 执行游标，并可在崩溃后从中断段恢复。
- **版本**：V28.8 六段导演台 → V29 六段 + PreBake。
- **测试**：六段真实生成 SUCCESS（见 `benchmarks/runs.csv`）；崩溃恢复测试（前 3 段文件不变，从第 4 段恢复）PASS。
- **核实**：`VERIFIED_BY_TEST`（8197 冻结线）；8207 线为独立演进且不在公开包内，标注 `DECLARED_NOT_FULLY_VERIFIED`。

## 3. 连续视频生成调度 【A】

- **用途**：一次提交连续产出六段并自动衔接，而非逐段手工点击。
- **设计特点**：`execution.continuous` 默认 `false`（安全默认），显式批量按钮会自动开启；保留文本、单段使用、SUCCESS、predecessor、eligibility 与 auto-merge 门控。
- **源码**：`H3_Prompt_Sidecar/web/h3_six_execute.js`、`six_ui.js`、`six_resume.py`。
- **与上游差异**：新增执行态初始化与「连续」显式授权路径，修掉了默认 `continuous=false` 导致批量按钮被 guard 拒绝的 NOOP 缺陷。
- **测试**：18 项 DOM/mock 回归 PASS；真实 8197 点击到 native merge / plan HTTP200。
- **核实**：`VERIFIED_BY_TEST`。

## 4. 上一段 AV Latent 接续 【C】

- **用途**：第 N+1 段沿用第 N 段的音视频潜空间，保证人物/服装/场景/机位跨段一致。
- **设计特点**：画布子图 `New Subgraph连续-封装`（8 节点）内用 `LTXVSeparateAVLatent` → `LTXVConcatAVLatent` 拆分/拼接；`Generate` 图在 PreBake 命中时不加载 Node136/CLIPLoader。
- **源码**：`workflows/current/V29_chinese_director_production_8197.json`（`definitions.subgraphs`），节点 `LTXVSeparateAVLatent`（1）/ `LTXVConcatAVLatent`（1）。
- **与上游差异**：Core 提供分离/拼接原语，但「按段编排 + 与 PreBake 缓存联动 + 未知 ancestry 自动 fallback」是本仓库的编排设计。
- **测试**：SEG2 真实续接 SEG1 latent，H3 重读 0 字节、TE 未重新执行；5 个接缝源-合并像素一致。
- **核实**：`VERIFIED_BY_TEST`（8197）。

## 5. Conditioning PreBake 缓存、失效与恢复 【A】

- **用途**：把六段文字的 conditioning 提前烘焙缓存，避免每段重复过 TE；并在文字/参考变更时正确失效。
- **设计特点**：缓存键 = 故事 ID + 段号 + 文字修订号 + 参考槽 SHA + H3/TE/VAE 身份；未知/动态 ancestry 自动 fallback 到常规路径。
- **源码**：`custom_nodes/local_author/8197_production_line/h3_conditioning_prebake/`：
  - `nodes.py`（节点定义）、`production.py`（生产逻辑）、`cache_codec.py`（缓存编解码）、`attempt_lifecycle.py`（尝试生命周期）、`observer.py`（观察器）、`model_registry.json`（模型身份登记）、`web/production.js`
- **与上游差异**：上游 ComfyUI 无按段 conditioning 缓存；该机制（含回执失效语义）为原创。
- **版本**：`H3_CONDITIONING_PREBAKE_V1`，`extra.h3_prebake_production = {enabled:true, static_ref2va_only:true}`。
- **测试**：离线回归 26 项 PASS —— 缓存写入中断后从第 4 段恢复（前 3 段文件不变）、旧 group/prompt/latent 回执拒绝、改段文字→该段及后续旧视频回执失效；SEG1 真实通过 608×1056/192 帧/24fps/8 秒，首次 H3 加载 20,873,793,024 字节。
- **核实**：`VERIFIED_BY_TEST`。

## 6. 自动六段视频合并 【A】

- **用途**：六段 SUCCESS 后自动触发合并，产出完整视频。
- **设计特点**：合并门控等待六段全部 SUCCESS 后约 2 秒触发；合并前校验接缝源。
- **源码**：`custom_nodes/local_author/8197_production_line/H3_Prompt_Sidecar/native_merge_control.py`、`web/h3_native_merge.js`、`web/h3_native_merge_template.json`（8207 线 `native_merge_control.py` 为独立演进版，未随本仓库发布）。
- **与上游差异**：Core 的 `CreateVideo`/`SaveVideo` 无自动六段合并编排；本实现新增门控、接缝校验与产物登记。
- **测试**：合并产物 39.875 秒（六段）、41.5 秒（验收组），996 帧/24fps/608×1056，5 个接缝人物/服装/场景/机位全程一致。
- **核实**：`VERIFIED_BY_TEST`（8197）。

## 7. 工作流安全门控与运行回执校验 【A】

- **用途**：拒绝过期/被改写的执行回执，防止用旧产物冒充新结果。
- **设计特点**：group / prompt / latent 三级回执；改段文字即令该段及后续旧视频回执失效；新 cache 缺失时 generate 返回 HTTP409 安全拦截（不静默跑错分支）。
- **源码**：`h3_conditioning_prebake/cache_codec.py`、`attempt_lifecycle.py`；工作流 `extra.h3_output_contract = "sampled-primary-output-v1"`、`extra.h3_prebake_production`。
- **测试**：旧 group/prompt/latent 回执拒绝 PASS；cache 缺失 generate HTTP409 拦截 PASS。
- **核实**：`VERIFIED_BY_TEST`。

## 8. 显存 / 内存生命周期工程化 【A（标注运行时耦合，见 §14-1/§14-2）】

> **归属修正**：本文早期版本把该项标为 `B`。按统一后的类别定义，`B` = "上游组件以外部依赖形式安装"（如 `H3_AudioUpgrade`）；本项的上游组件（ComfyUI / `comfy_extras`）是**运行时宿主**、并未被搬运或改装，其自研部分（精确身份 + 零驻留 + peer 保护 + 回退父 patcher）全部由本作者编写，故归 `A`，并在 §14 登记运行时耦合。此修正已同步到 `manifests/nodes.csv`。

- **用途**：在有限 RAM/显存下让 32B 级 TE + H3 主模型可稳定跑完六段。
- **组成与源码**：
  - `h3_adaptive_host_warm_inplace/__init__.py` —— Adaptive pre-TE release：不以 PDD clone 的 308 个 patch 作为放行前提，支持官方 `LoadedModel` 回退父 patcher；精确身份、测量、零驻留、peer 保护。
  - `h3_selective_te_unload/__init__.py` —— TE selective unload。
  - `h3_selective_diffusion_unload/__init__.py` —— diffusion 选择性卸载。
  - `h3_partial_diffusion_evict/__init__.py` —— VAE 前的部分驱逐。
  - `h3_sampler_to_vae_residency_probe/`、`h3_te_residency_probe/`、`h3_transfer_audit/` —— 驻留/搬运审计探针（用于取证，不参与生产执行）。
- **与上游差异**：基于上游 H3 运行时与 PDD-Acc 的加载/卸载机制做二次开发，新增「精确身份 + 零驻留 + peer 保护 + 回退父 patcher」；不改上游语义，仅改变释放时机与判定前提。
- **测试**：三条真实路径（cache 命中 / 未命中 / 冷启动）验收通过并晋升；热路径 Commit 峰值 90.215%，`MEMORY_MARGIN = LIMITED`（**明确不宣称内存无忧**）。
- **核实**：`VERIFIED_BY_TEST`（8197）；8207 线未做同等 GPU 验收且不在公开包内 → `DECLARED_NOT_FULLY_VERIFIED`。

## 9. 模型 / 采样 / 参考素材多路线管理 【C】

- **用途**：用中文选择器矩阵切换生成模式、图片模式、Ref2VA 后端、注意力档位、速度档位、FL2V 路由、分辨率与操作。
- **设计特点**：五路注意力分列（禁止用"稀疏注意力"总称指代单一档位）：FastH3 VSA / SLA / Sage Attention / INT8 内置量化核 / BlockSparseAttention（实验）。
- **源码**：工作流内 `H3*Selector` 节点群 + `extra.h3_attention_routes`；后端执行体为 Core 原生与第三方节点（`MiniMaxH3MemoryEfficientSageAttentionPatch`、`BlockSparseAttention`、`Ref2VAVSAGatePatch`、`MiniMaxH3PDDAccApply`）。
- **归属说明**：**执行算法归上游，路线编排与中文语义分层归本作者**。
- **核实**：`VERIFIED_BY_SOURCE`；部分实验档位（SLA、BlockSparse）仅登记架构位置，未验收 → `DECLARED_NOT_FULLY_VERIFIED`。

## 10. 自研前端控制层 【A】

- **用途**：中文导演台 UI、六段面板、开关持久化、GUIDE 权威归一。
- **源码**：`custom_nodes/local_author/8197_production_line/H3_ChineseDirectorUI/js/chinese_director.js`、`H3_Prompt_Sidecar/web/*.js`、`H3_Audio8Step/web/audio8.js`、`H3_AudioUpgrade/web/audio_upgrade.js`、`H3_NextgenDirector/js/h3_guide_timeline.js`（以上均在公开包内；8207 UI 线不在公开包内）。
- **设计特点**：
  - GUIDE 权威归一：总控台 `setSwitch` 与 `H3GuideModeSelector`（节点 991）保持同源，helper sync 无法再把 GUIDE OFF 翻回。
  - 开关持久化：`COMFYUI_FRONTEND_VERSION_LOCK = 1.52.7`（1.53.6 存在 tab 切换恢复 `mode=0` 的已知回归，升级前必须加门禁）；`TAB_SWITCH_MODE_PERSISTENCE = PASS`（1.52.7 实测切走/切回双态保持）。
- **与上游差异**：基于 ComfyUI 前端扩展机制自研，未修改 ComfyUI 前端源码；8207 冻结件与 8197 线在 `chinese_director.js` 上有差异（8197 线含 GUIDE 权威补丁；**8207 冻结件不含该补丁、已停止使用，且不在公开包内，不应作为前端代码源**）。
- **核实**：`VERIFIED_BY_TEST`（8197，1.52.7 实测）。

## 11. 音频链路（H3_Audio8Step / H3_AudioUpgrade）【A / B】

- **用途**：H3 音频 8 步与音频升级路线的前端/节点支持。
- **源码**：`custom_nodes/local_author/8197_production_line/H3_Audio8Step/{nodes.py, web/audio8.js, __init__.py}`（【A】）、
  `H3_AudioUpgrade/{nodes.py, web/audio_upgrade.js, __init__.py, audio_refine_loader.py}`（包装层 【B】）。
- **外部依赖（重要）**：`H3_AudioUpgrade` 运行需要上游采样器 `H3AudioRefineSampler`，来自
  `Adudeguyman/ComfyUI-H3-AudioRefine`（**MIT**），钉在 commit `fd5a8dfe8b4c636b1877abd07d11ebc985eddbed`
  （`nodes.py` blob `4b8e966f330cb96dfab75b9aeab5ae952c236972`，LF 归一化 SHA256 `1e2cc221…`）。
  **公开包不含 `vendor/`**：用 `python scripts/setup/install_h3_audio_refine.py --source <副本>` 装到包外目录。
  缺失时抛 `H3AudioRefineMissing`，消息内含上游地址、许可、commit 与 `git clone` 命令；**不返回桩实现、不静默跳过**。
- **核实**：`VERIFIED_BY_SOURCE` + `VERIFIED_UPSTREAM_API`（上游仓库与 MIT 许可经 GitHub API 核实 2026-10-13）；
  音频路线在 V29 中为可选分支，未作为主验收范围 → 部分能力 `DECLARED_NOT_FULLY_VERIFIED`。
  **本轮未做 GPU 运行验证**，依赖解析与缺失报错只做了**静态与导入级验证**。

## 12. 连续/原生接续（H3_NativeContinuation、H3_NextgenDirector）【A】

- **源码**：`H3_NativeContinuation/{core.py, nodes.py, __init__.py}`、`H3_NextgenDirector/{nodes.py, js/h3_guide_timeline.js, __init__.py}`。
- **用途**：原生接续与 NextGen 导演台（含关键帧时间线 `H3GuideTimeline`）。
- **核实**：`VERIFIED_BY_SOURCE`；`H3GuideTimeline` 的关键帧时间线在 8197 生产未启用（8207 线候选不在公开包内）→ `DECLARED_NOT_FULLY_VERIFIED`。

## 13. 工作流本身作为工程成果 【C】

- `workflows/current/V29_chinese_director_production_8197.json`：181 节点 / 218 连线 / 2 个子图，76 种节点类型，是本作者从 V16 起逐版演进、编译、裁剪与门控的产物，也是**本仓库唯一公开发布的工作流**（Git blob SHA `aadee988ad2cce4d946e9054643a72f4d0e41d6b`，blob 字节 SHA256 `311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`）。
- 逐节点隐私审计：全部 181 个顶层节点与 2 个子图内 15 个节点的字符串叶子（共 15,911 条）逐项检查，结果为用户图片 0、个人剧情提示词 0、六段导演文字全空、私人路径/素材名/身份/运行回执 0、未定义节点类型 0；连线表与结构逐项与生产原件对拍为**同拓扑**（差异只发生在被替换的文本值上）。断言脚本见 `tests/`。
- **原创性边界（不得表述为"全部原创"）**：这 2 个子图中，**1 个是 SDPose 官方 blueprint 的派生件**（【E】，见 §16），
  不计入本作者原创；另一个（`New Subgraph连续-封装`）为本地作者编排。工作流整体的原创性体现在
  **接线拓扑、六段状态机、合并时序与门控**，而不是"每一个子图都是原创"。
  因此本仓库不再使用"所有子图完全原创""不包含任何第三方内容"一类表述。
- 演进链（历代工作流、历史报告与 SHA 台账）**不再公开**，仅保留在生产侧本机归档；公开版不复述其内容，以避免历史 JSON/日志夹带个人创作内容。

---

## 14. 修改上游运行行为的自研模块（版本耦合 / 兼容性 / 上游依赖）【A，但标注耦合】

以下 8 个自研模块**调用或覆写** ComfyUI / 上游 H3 运行时的行为。它们的原创部分（判定逻辑、身份契约、时机控制）归本作者，但**功能可用性依赖上游未变更**。这里登记耦合对象与上游变更时的失效表现，**不**把它们判为 GPL 派生（未复制上游源码）。

| # | 模块 | 耦合对象 | 上游变更时的失效表现 |
|---|---|---|---|
| 1 | `h3_adaptive_host_warm_inplace/__init__.py` | `nodes.NODE_CLASS_MAPPINGS['MiniMaxH3ReferenceToVideo']` + `comfy_extras/nodes_minimax_h3.py` 的源文件路径与类名 | 导入即 `raise RuntimeError('Registered Node136 is not the official source class')`；上游改名/换路径 → 节点整包加载失败 |
| 2 | `h3_adaptive_host_warm_v1.disabled/__init__.py` | `from comfy_extras.nodes_minimax_h3 import MiniMaxH3ReferenceToVideo`（已禁用） | 同上；已以 `.disabled` 停用，不影响生产 |
| 3 | `H3_NextgenDirector/nodes.py` | `from comfy_extras.nodes_minimax_h3 import MiniMaxH3AddGuide` | 上游移除/改名 `MiniMaxH3AddGuide` → ImportError |
| 4 | `h3_transfer_audit/__init__.py` | `from comfy_extras.nodes_minimax_h3 import _resize, CANVAS_MULTIPLE`（私有符号） | 上游重命名私有符号 → 探针失效（诊断件，不阻断生产） |
| 5 | `H3_NativeContinuation/core.py` | 复刻 `comfy_extras/nodes_minimax_h3.py` 的时间线算术 | 上游改帧数/时间线语义 → 接续偏移错位（**逻辑复刻，属行为对齐，不是源码复制**） |
| 6 | `h3_conditioning_prebake/production.py` | `from comfy_extras.nodes_resolution import ResolutionSelector`；`from comfy_extras.nodes_math import MathExpressionNode` | 上游改名 → PreBake 生产路径导入失败 |
| 7 | `H3_AudioUpgrade/nodes.py` | `from comfy_extras.nodes_custom_sampler import BasicScheduler`；`from comfy_extras.nodes_audio import LoadAudio`；以及外部上游 `H3AudioRefineSampler` | 前两者改名 → 导入失败；后者缺失 → 抛 `H3AudioRefineMissing`（含安装命令），**不**静默降级 |
| 8 | `h3_workflow_helpers/tests/test_native_reference_payload.py` | 读取并 AST 执行 `comfy_extras/nodes_minimax_h3.py` 的 `MiniMaxH3ReferenceToVideo.execute` | 该文件**必须放在 ComfyUI 目录树内**（`parents[3]/comfy_extras/`）才能运行；仓库外单独运行会 FileNotFoundError。属测试用例的上游耦合，非生产依赖 |

> 第 8 项是一个**已知的可用性边界**：该测试只在完整 ComfyUI 部署内可运行，公开仓库单独 clone 后运行会失败。已在 `REMAINING_HOLD.md` 登记为 `HOLD-TEST-ENV`，**未**通过删除该测试来制造"全绿"。

## 15. MiniMax 官方 H3 提示词 Skill —— 已识别为第三方原版并从公开包移除【D，`LICENSE_HOLD`】

- **位置**：`custom_nodes/local_author/8197_production_line/H3_V28_Director/skills/official-minimax-h3-prompt/`
- **三份文件**：`SKILL.md`、`references/base-en.txt`、`references/ref-en.txt`
- **判定依据**：与 `MiniMax-AI/MiniMax-H3` 仓库 `skills/h3-prompt-writing/` 下同名文件的 Git blob（LF 归一化后）**逐字节相等**
  （blob `b6d9b283…` / `40cf586a…` / `7ae1b2d0…`）。
- **许可状态**：`LICENSE_HOLD`。上游 GitHub API `license == null`（无 SPDX）；模型与 Skill 走 Hugging Face *MiniMax Community License Agreement*，含地域与商业限制。**本仓库不对其授 MIT，不重分发。**
- **处理**：三份文件已从公开包 `git rm`；目录内保留 `README.md` 记录来源、版本、Git SHA、比对证据、依赖解析顺序与安装命令。
- **运行时依赖**：`v28_h3_format` **确实**在运行时解析 `references/ref-en.txt`（六段标题、`TASK_TYPES`、`VISIBLE_MARKERS`、`AUDIO_MARKERS`）。改为：
  - 环境变量 `H3_MINIMAX_OFFICIAL_SKILL_DIR` 指向用户自行获取的官方副本；
  - 或把副本放回原目录；
  - 缺失时抛 `H3OfficialGuideMissing`（含上游地址、许可 HOLD 说明、安装命令），**不**返回桩、**不**静默降级。
  - 模块级改为 PEP 562 `__getattr__` 懒加载：包可以正常导入，只在真正用到 guide 常量时才报错。
- **未做**：未在未取得授权前自动下载、捆绑或重分发官方原版文件。

## 16. SDPose 多人姿态子图 —— 官方 blueprint 的派生件【E，**不是完全原创**】

- **位置**：唯一工作流 `workflows/current/V29_chinese_director_production_8197.json` 的 `definitions.subgraphs[1]`
- **上游**：`Comfy-Org/workflow_templates`（仓库根 LICENSE = **MIT**），
  commit `cdccb2ee7a7cd0baee4630cf7186283a98ab408f`，
  路径 `blueprints/video_to_pose_map_sdpose_multi_person.json`，
  blob `6f6d7ab146a5b143f70bc98d444a7a64829a94ea`，size `33268`，
  SHA256 `92e31fb99f4a005a9263c296429c99eb0847567d64b1f3a35fa42839e0cbfec2`
- **判读**：官方文件是 workflow wrapper（顶层 1 个占位节点），蓝图本体在 `definitions.subgraphs[0]`。
  全等部分：inputs 15/15、outputs 5/5、节点 7/7、连线 28/28；本项目修改：**80 处节点叶子 + 10 处连线叶子**（含 id/name 改写）。
- **许可边界**：ComfyUI 宿主是 GPL-3.0，但 GPL **不自动延伸**到这个独立的 MIT 仓库。该子图按上游 MIT 分发并附修改声明。
- **已修正的过宽表述**：旧文档称其为"基于 `Comfy-Org/SDPose` 官方模型与社区子图结构、本仓库保留其结构"——上游坐标错误且未给出版本，已更正为上述钉住坐标。
- **未做**：**没有修改**唯一 V29 工作流 JSON（blob `aadee988ad2cce4d946e9054643a72f4d0e41d6b` 保持不变）。

---

## 明确不属于本作者原创的部分

- **MiniMax-H3 模型与权重**（Comfy-Org / MiniMaxAI）—— 不随包分发
- **ComfyUI 引擎本体与其内置节点**（Comfy-Org，GPL-3.0）—— 不搬运源码；本仓库仅引用其运行时与节点类型名，见 §14
- **MiniMax 官方 H3 提示词 Skill 三份原版文件**（MiniMax-AI）—— 已移除，见 §15
- **SDPose 多人姿态子图**—— 官方 MIT blueprint 的**派生件**，不是完全原创，见 §16
- **第三方节点**：`ComfyUI-KJNodes`(kijai)、`rgthree-comfy`(rgthree)、`ComfyUI-MAINodes`(matlowai)、`ComfyUI-Ref2VA-VSA`(Kablex)、`ComfyUI-MiniMax-H3-PDD-Acc`(Jalen-Brunson)、`ComfyUI-H3-Motion-Context`(NikoDemon80)、`H3-Optimizations`(Zironic)、`comfyui-obvpm`(obvpm)、`comfyui-anthropic-claude`(alexmunteanu)、`comfyui_claude_prompt_generator`(PauldeLavallaz)、`ComfyUI-Krea2Edit`(conradlocke/lbouaraba)、`krea-reference`(kgilper)
- **ComfyUI-H3-AudioRefine**（Adudeguyman，MIT）—— **外部依赖**，不随包分发，见 `THIRD_PARTY_NOTICES.md` §2c

> 其中 `H3-Optimizations`(Zironic) 与 `comfyui-obvpm`(obvpm) 的上游仓库**未附带 SPDX LICENSE 文件**，许可只能按仓库内声明文本判断，已标 `LICENSE_HOLD`，不做无依据的法律定论。

明细见 [`docs/UPSTREAM_ATTRIBUTION.md`](docs/UPSTREAM_ATTRIBUTION.md)、[`manifests/nodes.csv`](manifests/nodes.csv) 与 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
