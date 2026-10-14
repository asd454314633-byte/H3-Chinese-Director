# H3 中文导演台 V29.4｜完整功能、模式与验收索引

> **版本边界**：本文件针对 `H3-Chinese-Director` 的**8197 V29 冻结生产线 / v29.4 公开源码包**。2026-10-14 审计对象为 `workflows/current/V29_chinese_director_production_8197.json`，**181 个顶层节点 / 218 连线 / 2 个内嵌子图**；仓库包含 **141 个 `custom_nodes/local_author/8197_production_line/` 下的文件**（包含 Python、JS 和资源，**不是 141 种节点或 141 项原创功能**）。
>
> **读者须知**：区分「工作流含有节点/选择器」「可手动启用」「历史测试通过」「当前版本完整测试通过」。已接线但默认旁路、研究占位、未重新验收的功能**不能**统称稳定可用。公开包不含模型权重、私人素材及第三方完整运行环境。

## 1. 五类真正的产品能力

| 能力领域 | 对外可理解的能力 | 关键位置与边界 |
|---|---|---|
| 中文统一操作 | 用 `N159 H3OperationSelector` 作为主要入口，集中配置生成操作、素材、模型/采样策略；不必逐个改底层执行节点 | `H3_ChineseDirectorUI/js/chinese_director.js`，`H3OperationSelector` |
| 六段剧情管理 | 六段独立编辑；选择使用/执行；控制连续、独立起点、开始段和续跑；每段结果、编辑草稿与状态分别管理 | `H3SixDirectorState`、`six_prompt_state`、`H3_Prompt_Sidecar/web`；仅实际成功结果可晋升前序 |
| Native 视频接续 | 利用**前段真实 AV latent**建立续接，校验前段身份，不是简单拼接上一段 MP4 或仅复用最终画面 | `H3_NativeContinuation`、`LTXVSeparateAVLatent` / `LTXVConcatAVLatent` 编排 |
| 缓存与资源治理 | Conditioning PreBake；根据故事、段号、文字修订、参考槽、模型身份校验缓存；TE 卸载、Host Warm、VAE 前部分释放 | `h3_conditioning_prebake`、`h3_adaptive_host_warm_inplace`、`h3_selective_te_unload`、`h3_partial_diffusion_evict` |
| 结果与安全 | 六段满足 SUCCESS/身份门禁后自动合并；旧 group/prompt/latent receipt 不可任意冒用；错误前序、缺缓存拒绝 | `H3_Prompt_Sidecar`、`H3_V29_ManualChainMerge`；历史验收有自动合并证据 |

## 用户能直接看见的 N159 操作阶段与独立路线

N159「H3 全中文傻瓜导演台」不只是六段剧情输入框。**公开源码 `H3OperationSelector.MODES` 共六个 UI 状态**（其中第五项为实验自动化、第六项为关闭/无选中状态）：

| N159 操作 | 实际操作含义 | 可用性边界 |
|---|---|---|
| **只跑一采** | 主模型采样并输出新视频，坏段检测与二采链旁路 | 正式一采基线 |
| **检测坏段** | 计算高速动作异常区间/曲线并输出检测报告 | 本模式不启动扩时或二采 |
| **放大/扩时** | 仅建立扩时预览与方案报告 | 不进行后续二采 |
| **执行二采** | 对扩时/初始潜空间做独立修复采样 | 用于已配置对应输入的修复链；不等于默认自动执行 |
| **自动检测+扩时+二采（实验）** | 检测后按坏段条件开启窗口二采，无异常时直通结果 | **实验模式**，不宣称任意视频都验证通过 |
| **无任何选项状态** | 所有运行分支旁路 | 非正常视频生成模式 |

这些是「**操作阶段**」，与「生成模式」「一采速度档」「Ref2VA 后端」「注意力」「尺寸」「Guide/连续增强」等**彼此独立的控制轴**，不能把不同控制轴的名称混为一张互斥菜单。

另有两项经常被忽略的功能：**前端操作阶段卡片有独立执行按钮**，并对已点亮节点做可视化提示；**FL2VA 的 F4 与 FastH3 V2 是两条路线，Ref2VA 的 Stable8 与 PDD8 又是另一条分支族**。核心源码：[H3OperationSelector/路由声明](../custom_nodes/local_author/8197_production_line/h3_workflow_helpers/nodes.py)、[前端多模式卡片](../custom_nodes/local_author/8197_production_line/h3_workflow_helpers/web/h3_workflow_ux.js)。

## 2. 工作流的模式与技术路线（直接核对 JSON）

### 2.1 视频生成 / 图片输入 / 素材模式

| 切换层 | 公开 JSON 中的节点与选项 | 性质/使用边界 |
|---|---|---|
| 生成模式 | `H3GenerationModeSelector`：多参考图 `REF2VA` 与 `FL2VA` 家族路线 | 模型和 Conditioning 的**实际路由选择**，非单纯 UI 标签 |
| 图片模式 | `H3ImageModeSelector`：无图文生视频；单图与首尾帧由 `MiniMaxH3ImageToVideo` 与对应输入组合 | `FL2VA` 路线；**不能把单图 FastH3 VSA 4 步误称为四图 Ref2VA** |
| 多参考素材 | `MiniMaxH3ReferenceToVideo`、`H3ReferenceSourceSelector`：参考图片、参考视频、参考音频的选择；公开画布还有 1–9 参考图槽位 | **存在槽位 ≠ 每个槽位在所有后端生效**；按所选分支及实际支持的输入检验 |
| 参考视频 V2V/RV2V | `H3V2VInit`、`H3WindowLoop`、上传视频等节点保留；参考视频/图/音组合用于 V2V/RV2V 编排 | `docs/FEATURE_MATRIX.md` 标 `PARTIAL`；公开默认旁路，**不是正式端到端验收能力** |
| 分辨率 | `ResolutionSelector`、`H3SizeModeSelector`，预设尺寸/自定义尺寸，32 倍数对齐；工作流初始选择 9:16、0.6MP | 可见控制与执行尺寸相关；实际分辨率受模型/依赖约束 |
| 输出与音频 | 视频 VAE + 音频 VAE、`CreateVideo` / `SaveVideo`，24fps 基线；可选参考音频预检、Audio8Step 与 AudioUpgrade | 普通视频/音频链路不等于**音频 8 步或精修链已完整验收**；后者为 `PARTIAL` |

### 2.2 多采样/加速模式（不是同一条分支）

| 路线 | 工作流节点 / 样例参数 | 准确状态 |
|---|---|---|
| 一采「默认（原样）」 | `H3SpeedModeSelector`；原始链 `er_sde` 等 | 原生产选择器内的基线路线 |
| 一采「画质优先」 | 独立的 `res_multistep` 采样器选择 | 有隔离的选择器与执行位，不能以名称推断所有内容优于默认 |
| 一采「高速平衡」 | `euler`、Sage Attention、INT8 VAE 等针对该路线的分支 | 有执行位；性能/画质需要**同条件对比**，不可宣称普遍提速比例 |
| Ref2VA 正式后端选择 | `H3Ref2vaBackendSelector` 当前公开菜单：**稳定多参考8步 / PDD多参考8步 / Native Ref2VA 20步诊断** | Stable8/PDD8 曾有真实视频验收；20步是高级诊断，**不是推荐生产默认路线** |
| Ref2VA VSA 历史兼容链 | Turbo 4-step LoRA、VSA Gate、Sigma 12/3 等相关节点仍留在画布 | **当前 Ref2VA 后端菜单已隐藏旧 VSA/Original 选项，仅保留回滚兼容节点；不得将其宣传为现在可选的主生产档** |
| Ref2VA PDD 8-step | `MiniMaxH3PDDAccApply`、8步、Euler、PDD Acc；可切标准或 INT8 Attention | 公开 JSON 默认显示 `PDD多参考8步` 选择器值；受真实节点、模型、许可和版本约束 |
| FastH3 V2 8-step | `UNETLoader` + `MiniMaxH3SigmaShift` 视频 10 / 音频 3 + Core VSA + simple 8 步 + `res_multistep` | **工作流保留、默认关闭**；不可当作本公开版 GPU 验收结果 |
| **FL2VA FastH3 F4（4步）** | `H3Fl2vRouteSelector`：F4（社区V1重打包）；`MiniMaxH3ImageToVideo`（文生/单图/首尾帧家族） | **F4 是 FL2VA 二级路线**，不是当前 Ref2VA 后端菜单；多图 Ref2VA 成功不能由本项推导 |

### 2.3 五路注意力技术：明确区分

| 名称 | 典型节点/路线 | 公开状态 |
|---|---|---|
| FastH3 VSA 超稀疏视频分块 | `Ref2VAVSAGatePatch` | 保留 VSA 路线，不等于所有分支启用 |
| SLA 混合线性稀疏 | 路线占位 | **无执行体、未安装、不可运行** |
| Sage Attention 量化核 | `MiniMaxH3MemoryEfficientSageAttentionPatch` | 高速路线专用，默认旁路 |
| INT8 Attention 内置量化核 | `ModelAttentionBackend` | PDD 8步的可选加速开关，不能推广给全部后端 |
| Core BlockSparseAttention | `BlockSparseAttention` | 实验/隔离位，**不等于已接入默认生产链** |

### 2.4 其余高级能力和候选模块

- **GUIDE 关键帧时间线**：`H3GuideTimeline`、图像未配置门禁与 `H3GuideModeSelector` 存在，但 **8197 冻结生产未启用/未按此路线进行 GPU 验收**；前端开关持久化及 GUIDE 状态权威归一有单独测试，不代表关键帧动态质量通过。
- **坏段检测**：`H3JerkOracle` 对高速动作/异常时间区间进行分析；公开 JSON 包括人工 hold-map。
- **扩时/插帧式时间处理**：`H3TimeSmear` 以及恢复时间轴的 `H3ExactRecover` 等处理节点在工作流内存在，部分**默认关闭**。
- **二采与自动窗口修复**：`H3V2VInit`、`SamplerCustomAdvanced`、`H3WindowLoop`；存在手工/自动修复画布区域，但不等于当前默认一采路径必然执行二采。
- **Progressive / SelfLift 高分辨率增强**、**SLA**：只登记架构槽位，**不能宣传为已实现的可执行模式**。
- **采样实时预览**：`ModelPreviewOverrideKJ` 提供可配置的预览接口，效果依赖对应插件与本机环境。
- **可选 AI Director / 提示词编译**：仓库含 V28 导演/Sidecar 等控制层；特定语言模型后端、官方提示词 Skill 及第三方音频精修需单独配置，不是 H3 手工编辑六段提示词的强制前置条件。

## 3. 用户实际使用与更多可核对的能力（2026-10-14 补录）

本节将两种证据**同时保留**：一是仓库公开的节点和参数，二是项目所有者对真实生产使用的明确确认。后者是**用户亲历的使用证据**，不是未经公开回执独立核验的 GPU 测试次数。

### 3.1 音色克隆参考：已实际使用、用户确认长期稳定

**项目所有者 2026-10-14 明确确认：H3 导演台的音色克隆/参考音色能力已经过实际生成测试，并长期稳定使用。** 因此它不是“未实测才待实现”的功能，应列为**生产中使用的参考音色能力（OWNER_CONFIRMED_LONG_TERM_USE）**。目前在本公开包中，尚未提供按音色槽独立标记的脱敏 GPU 回执与音色保真对比音频；**公开复核证据 = SOURCE_VERIFIED + OWNER_CONFIRMED，独立可公开 E2E 数量 = NOT_DOCUMENTED**，不得反向写成“用户没测试过”。

具体实现（均可在仓库核对）：

| 已有控制 | 真实源码与使用语义 | 边界 |
|---|---|---|
| **音色参考 1 / 2 / 3** | `H3Audio8ReferencePreflight`、`H3AudioReferencePack`；`ref_audios.ref_audio_0..2`，分别启停与映射 | **3 个音色参考槽**，不等于同一时刻三人同时说话的质量逐项已公开评分 |
| **视频原音轨参考** | `soundtrack_enabled`、`ref_video_audios` 和 `<VideoSoundtrack>` 独立标识 | 只在相应 Ref2VA/参考视频条件下启用，不能当成独立人声克隆槽 |
| **声音/角色对应** | 提示词中的 `<Audio 1/2/3>` 自动映射实际源顺序，独立 `role3` 角色描述 | 编号与说话人关系需保持一致；避免角色与人声交叉 |
| **输入预检** | 单条音色音频 2–15 秒；启用参考音频合计 ≤15 秒；检查时长、通道和无效波形/未连接槽位 | 8 步参考预检只检查，不裁音、不重采样/不改 PCM |
| **8 步音色路线** | `H3_Audio8Step/web/audio8.js` 约束 Stable8 / PDD8 后端，开启参考槽、注入合法 ref_audios 边 | 路线有源码与用户实际使用确认；具体新增组合仍以逐次实际生成验证 |
| **音频专项升级（不同功能）** | `H3_AudioUpgrade` 包括音频质量档、指定音轨驱动、音频精修、已缓存一采精修、最终输出路由 | **不是音色克隆的同义词**，外部 AudioRefine 依赖需要单装，部分属于候选/未完整验收 |

参考音色用于引导新生成对白的音色特征，和**原音轨复制/指定 TTS-WAV 驱动**不同。MiniMax 官方 H3 Ref2VA 规范支持最多 3 份参考音频（单条 2–15 秒、总计 ≤15 秒），但这不能代替本地某个后端的 GPU 验收。对话、声效、背景音乐和视频音轨要按各自用途描述。

证据入口：[Audio8Step 真实预检源码](../custom_nodes/local_author/8197_production_line/H3_Audio8Step/nodes.py) · [Audio8Step 前端](../custom_nodes/local_author/8197_production_line/H3_Audio8Step/web/audio8.js) · [AudioUpgrade 前端](../custom_nodes/local_author/8197_production_line/H3_AudioUpgrade/web/audio_upgrade.js) · [AudioUpgrade 节点](../custom_nodes/local_author/8197_production_line/H3_AudioUpgrade/nodes.py)。

### 3.2 Clean Rebase + Guide：多时间点实验与已验收的单帧必须分开

**2026-10-09 冻结 8197 V29 的真实六段生产验收：第 4 段使用 Clean Rebase + 官方单张 Guide frame0**；Guide 图取自同组第 3 段的第 152 帧。测试记录包括六段真实 SUCCESS、五处视频接缝源-合并像素一致、3→4 主体高度对齐 0% 差异（仅在该测试口径/人物/镜头范围内），最终 `CLEAN_REBASE_GUIDE=PASS`、`VISUAL_CONTINUITY=PASS_WITHIN_TESTED_SCOPE`、`AUTO_MERGE=PASS`。**这项已验收，不能被笼统归入“GUIDE 全部未测试”。**

另一个不同能力是**多个时间点的 Guide Timeline 与拖动时间轴**（`H3GuideTimeline`）。工作流保留对应代码与默认关闭实验位，**8197 公开版没有为每个时间点组合提供同等 GPU E2E 验收**。Pose/Depth Fun ControlNet 同理：支持前端/节点与实验路线描述，但不能冒充六段生产 PASS。

### 3.3 Stable8 与 PDD8 两条路径都经过真实视频测试

2026-10-06 历史维修验收记录中的同条件分支对照：**Stable8 111.186 秒、PDD8 110.052 秒**；均为 **608×1056、192 帧、24fps、8 秒、8 步** 视频。Stable8 的非 PDD patch 情况与 PDD8 308 patches 分别检查，Node1058 与两路 VAE、最终视频解码通过；运行期间仍报告 `MEMORY_MARGIN=LIMITED`。这是**旧版本指定两条样本的真实运行**，不是“所有 VSA/Stable/PDD 音色组合都测试过”或通用性能平均值。

**其它可查的真实测试例子：** 2026-10-06 的资源/释放验收另有 608×1056、192 帧、8 秒、8 步、三参考 RUN1 139.189 秒与 RUN2 86.404 秒；不同上下文/初始化状态，**不能与上述两条直接混合计算加速比**。

### 3.4 连续生产的稳定性并非只有六段一次成功

历史维修记录还包含不同轮次的**18 项六段 UI DOM/mock 回归**、**90/90 生命周期离线回归**、**22/22 隔离浏览器回归**，以及 Guide 定点修复阶段的 **109/109、34/34、42/42** 风险与回归验证。它们覆盖了按钮初始化、持续任务、恢复、Guide/前序资格与资源治理，**不是可累计的独立 GPU 视频数量**，存在历史版本重叠，且最终上线范围以 2026-10-09 冻结正式验收为准。

### 3.5 其它容易漏掉的实际交互

- **Guide / Pose / 连续增强三个独立前端开关**；关键画面最多三个素材入口，未上传有效文件时可自动安全关闭；GUIDE 开关状态防止被 helper 重新意外打开。
- **图片与视频上传预检**、素材格式/源路径校验、已上传素材跨面板可见性；非法素材不会静默当作参考使用。
- **六段面板定位/控制台定位、可缩放 UI 与调整面板尺寸**；草稿编辑与后台执行身份隔离。
- **指定音轨驱动**：允许指定 WAV/TTS 音频作为独立最终音轨，要求原始音轨长度/音频 VAE 对齐；与参考音色和精修并非同一操作。
- **音频精修只读一采缓存**：前端存在“仅精修已缓存一采”的候选路径，减少为单独音频调整重复采样的必要性；外部依赖及实际音频效果仍需单独验收。
- **动态 Ref2VA 合同**：素材的图片/音频/视频槽与运行时引用边可被验证，避免角色参考编号漂移；V28 参考合同与公开单次六段 GPU 主流程的集成范围需要分开说明。

## 4. 数字说话：测试、验收、性能各算各的

### 4.1 8197 历史视频真实运行（不是 v29.4 新版全量 GPU 重跑）

| 项目 | 记录 | 口径 |
|---|---|---|
| 六段真实采样 | **132.926 / 92.423 / 90.368 / 87.255 / 91.070 / 90.277 秒** | 同一历史六段链中的 6 次结果，**单次记录，非平均值** |
| 六段自动合并 | **41.5 秒，996 帧，24fps，608×1056** | 历史自动合并记录，不等于所有时长/分辨率一致 |
| GPU 显存峰值 | **22,016 MiB** | 单次采样监控口径，不是稳定上限 |
| 最低可用 RAM / Commit 峰值 | **5.94 GiB / 95.05 GiB** | `MEMORY_MARGIN = LIMITED`，不宣传低内存无压力 |
| PreBake | **26 项离线回归 PASS** | 来自功能矩阵历史记录，不代表所有新内容命中缓存 |
| 六段连续性 | 历史真实六段 SUCCESS、SEG2 续接 SEG1 latent、接续链及合并通过 | **仅受测任务、版本和人物/镜头范围**，不保证任何新项目不会漂移 |

详见 [历史性能汇总](../benchmarks/SUMMARY.md) 和 [逐行 120 条基准记录](../benchmarks/runs.csv)。**120 是有不同证据等级的指标行，不是 120 次独立成功的视频测试；其中 108 条属报告抽取行、12 条属人工核对核心行。** 源报告定位采用 `LOCAL_ARCHIVE:`，原始私有档案不在 GitHub，外部读者无法独立复现全部证据。

### 4.2 v29.4 公开源码发布核查（区别于 GPU 效果验证）

| 验证类别 | 报告数字 | 能证明什么 |
|---|---|---|
| 发布验收门禁 | **33 PASS / 0 FAIL / 2 HOLD** | 包装、依赖、隐私、结构与拒绝错误配置的门禁；不等于 33 次视频生成 |
| V29 生产必需测试 | **13/13** 工作流结构、**7/7** 发布范围、**17/17** 门禁修复 | 三组独立源码/契约测试均 PASS；**不是 37 次 GPU 测试** |
| 隔离安装/故障注入 | **9/9 PASS** | 依赖导入、配置及清晰报错；未生成视频 |
| 公开 Python / JS / JSON / PowerShell | **121 / 25 / 10 / 2** 个文件语法检查 PASS（该报告覆盖范围） | 文件语法有效，不等于全功能测试 |
| V28 历史全量兼容套件 | **ran=285；F=16 / E=56 / skipped=14** | **存在既有失败**，与当时发布候选基线一致、无新增；不能宣传 285/285 PASS |
| 工作流结构保护 | **181 节点 / 218 连线 / 2 子图**；冻结 Git Blob `aadee988ad2cce4d946e9054643a72f4d0e41d6b` | 发布前的唯一工作流保持不变 |

证据：[v29.4 FINAL_GATE_REPORT](acceptance/FINAL_GATE_REPORT.md)、[逐项 33 PASS / 2 HOLD JSON](acceptance/acceptance_v29_4.json)、[功能矩阵](FEATURE_MATRIX.md)、[发布说明](RELEASE_NOTES.md)。**旧报告里的候选分支“尚未 push/Release”是当时的时间点记录；v29.4 后来已正式发布，不能把旧报告当成当前 GitHub 发布状态。**

## 5. 仍然需要诚实展示的限制

1. **v29.4 公开源码整改没有重新完成全新机器、全链路六段 GPU E2E。** 历史 8197 成功不自动证明任何用户的新部署结果。
2. **2 个 v29.4 发布 HOLD**：语义性脱敏占位符、冻结 JSON 的参考图/历史元数据占位符；发布前报告另记录了 V28 全量旧测试失败、部分上游许可边界。参考图须用户自己指定。
3. **真实功能 vs 占位**：音频升级、V2V/RV2V、关键帧、Fun ControlNet、SLA、Progressive 等不可统一列入“全部 PASS”。
4. **模型/版权**：官方 MiniMax H3 提示词 Skill 原版不随包分发（`LICENSE_HOLD`）；外部 AudioRefine/ComfyUI/其他节点另装并遵守各自许可证。参阅 [上游归属](UPSTREAM_ATTRIBUTION.md)。
5. **8197 ≠ 8207**：8207 独立实验预览见 [H3-8207-Experimental](https://github.com/asd454314633-byte/H3-8207-Experimental)，不能将 8197 的 GPU 结果套用到 8207 公开候选。

## 6. 使用与验证入口

**先了解功能** → [工作流结构](ARCHITECTURE.md) · [22 项功能矩阵](FEATURE_MATRIX.md) · [原创贡献归属](../AUTHOR_CONTRIBUTIONS.md)。

**准备安装** → [Windows 安装指南（历史文件名含 8207，但仅用于 8197）](INSTALL_WINDOWS_8207.md) · [模型表](MODELS.md) · [v29.4 Release](https://github.com/asd454314633-byte/H3-Chinese-Director/releases/tag/v29.4)。

**看真实数据** → [六段耗时、峰值与合并](../benchmarks/SUMMARY.md) · [发布验收及已知 HOLD](acceptance/FINAL_GATE_REPORT.md)。
