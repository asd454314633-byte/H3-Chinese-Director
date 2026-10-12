# 本地作者原创贡献清单（AUTHOR_CONTRIBUTIONS）

本文逐项给出：**用途 → 设计特点 → 确切源码路径 → 与上游项目的代码差异 → 首次/当前版本 → 关联测试与验收记录 → 归属类型 → 核实状态**。

归属类型定义：

- `A` 本地作者独立设计与自研实现
- `B` 在第三方代码基础上的二次开发（已说明差异与许可）
- `C` 本地作者原创工作流编排与系统集成（下游节点为第三方/Core）
- `D` 直接使用的第三方原版节点（不归于本作者原创）

核实状态：`VERIFIED_BY_SOURCE`（已比对源码）/ `VERIFIED_BY_TEST`（有测试或真实验收）/ `DECLARED_NOT_FULLY_VERIFIED`（功能存在但未完全验收，明确不谎称 PASS）。

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

## 8. 显存 / 内存生命周期工程化 【B】

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

## 11. 音频链路（H3_Audio8Step / H3_AudioUpgrade）【A】

- **用途**：H3 音频 8 步与音频升级路线的前端/节点支持。
- **源码**：`custom_nodes/local_author/8197_production_line/H3_Audio8Step/{nodes.py, web/audio8.js, __init__.py}`、`H3_AudioUpgrade/{nodes.py, web/audio_upgrade.js, __init__.py}`。
- **核实**：`VERIFIED_BY_SOURCE`;音频路线在 V29 中为可选分支，未作为主验收范围 → 部分能力 `DECLARED_NOT_FULLY_VERIFIED`。

## 12. 连续/原生接续（H3_NativeContinuation、H3_NextgenDirector）【A】

- **源码**：`H3_NativeContinuation/{core.py, nodes.py, __init__.py}`、`H3_NextgenDirector/{nodes.py, js/h3_guide_timeline.js, __init__.py}`。
- **用途**：原生接续与 NextGen 导演台（含关键帧时间线 `H3GuideTimeline`）。
- **核实**：`VERIFIED_BY_SOURCE`；`H3GuideTimeline` 的关键帧时间线在 8197 生产未启用（8207 线候选不在公开包内）→ `DECLARED_NOT_FULLY_VERIFIED`。

## 13. 工作流本身作为工程成果 【C】

- `workflows/current/V29_chinese_director_production_8197.json`：181 节点 / 218 连线 / 2 个子图，76 种节点类型，是本作者从 V16 起逐版演进、编译、裁剪与门控的产物，也是**本仓库唯一公开发布的工作流**（Git blob SHA `aadee988ad2cce4d946e9054643a72f4d0e41d6b`，blob 字节 SHA256 `311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`）。
- 逐节点隐私审计：全部 181 个顶层节点与 2 个子图内 15 个节点的字符串叶子（共 15,911 条）逐项检查，结果为用户图片 0、个人剧情提示词 0、六段导演文字全空、私人路径/素材名/身份/运行回执 0、未定义节点类型 0；连线表与结构逐项与生产原件对拍为**同拓扑**（差异只发生在被替换的文本值上）。断言脚本见 `tests/`。
- 演进链（历代工作流、历史报告与 SHA 台账）**不再公开**，仅保留在生产侧本机归档；公开版不复述其内容，以避免历史 JSON/日志夹带个人创作内容。

---

## 明确不属于本作者原创的部分

- **MiniMax-H3 模型与权重**（Comfy-Org / MiniMaxAI）
- **ComfyUI 引擎本体**（Comfy-Org）
- **第三方节点**：`ComfyUI-KJNodes`(kijai)、`rgthree-comfy`(rgthree)、`ComfyUI-MAINodes`(matlowai)、`ComfyUI-Ref2VA-VSA`(Kablex)、`ComfyUI-MiniMax-H3-PDD-Acc`(Jalen-Brunson)、`ComfyUI-H3-Motion-Context`(NikoDemon80)、`H3-Optimizations`(Zironic)、`comfyui-obvpm`(obvpm)、`comfyui-anthropic-claude`(alexmunteanu)、`comfyui_claude_prompt_generator`(PauldeLavallaz)、`ComfyUI-Krea2Edit`(conradlocke)、`krea-reference`(kgilper)
- **SDPose 多人姿态子图**基于 `Comfy-Org/SDPose` 官方模型与社区子图结构，本仓库保留其结构并标注来源

明细见 [`docs/UPSTREAM_ATTRIBUTION.md`](docs/UPSTREAM_ATTRIBUTION.md) 与 [`manifests/nodes.csv`](manifests/nodes.csv)。
