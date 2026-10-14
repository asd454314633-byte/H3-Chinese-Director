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
| Ref2VA 原始/参考路线 | `H3Ref2vaBackendSelector` 的原版分支 | 与 FL2VA 的单图/首尾帧区别对待 |
| Ref2VA FastH3 VSA | Turbo 4-step LoRA、VSA Gate、Sigma 12/3、Euler / simple 4 步等 | 独立 4 步路线；某些节点默认旁路；**不等于 FL2VA 四图参考** |
| Ref2VA PDD 8-step | `MiniMaxH3PDDAccApply`、8步、Euler、PDD Acc；可切标准或 INT8 Attention | 公开 JSON 默认显示 `PDD多参考8步` 选择器值；受真实节点、模型、许可和版本约束 |
| FastH3 V2 8-step | `UNETLoader` + `MiniMaxH3SigmaShift` 视频 10 / 音频 3 + Core VSA + simple 8 步 + `res_multistep` | **工作流保留、默认关闭**；不可当作本公开版 GPU 验收结果 |
| FL2VA FastH3 F4 | `H3Fl2vRouteSelector` 和 `MiniMaxH3ImageToVideo` | **首帧/首尾帧家族路线**，不能称为 Ref2VA 多图实测 |

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

## 3. 数字说话：测试、验收、性能各算各的

### 3.1 8197 历史视频真实运行（不是 v29.4 新版全量 GPU 重跑）

| 项目 | 记录 | 口径 |
|---|---|---|
| 六段真实采样 | **132.926 / 92.423 / 90.368 / 87.255 / 91.070 / 90.277 秒** | 同一历史六段链中的 6 次结果，**单次记录，非平均值** |
| 六段自动合并 | **41.5 秒，996 帧，24fps，608×1056** | 历史自动合并记录，不等于所有时长/分辨率一致 |
| GPU 显存峰值 | **22,016 MiB** | 单次采样监控口径，不是稳定上限 |
| 最低可用 RAM / Commit 峰值 | **5.94 GiB / 95.05 GiB** | `MEMORY_MARGIN = LIMITED`，不宣传低内存无压力 |
| PreBake | **26 项离线回归 PASS** | 来自功能矩阵历史记录，不代表所有新内容命中缓存 |
| 六段连续性 | 历史真实六段 SUCCESS、SEG2 续接 SEG1 latent、接续链及合并通过 | **仅受测任务、版本和人物/镜头范围**，不保证任何新项目不会漂移 |

详见 [历史性能汇总](../benchmarks/SUMMARY.md) 和 [逐行 120 条基准记录](../benchmarks/runs.csv)。**120 是有不同证据等级的指标行，不是 120 次独立成功的视频测试；其中 108 条属报告抽取行、12 条属人工核对核心行。** 源报告定位采用 `LOCAL_ARCHIVE:`，原始私有档案不在 GitHub，外部读者无法独立复现全部证据。

### 3.2 v29.4 公开源码发布核查（区别于 GPU 效果验证）

| 验证类别 | 报告数字 | 能证明什么 |
|---|---|---|
| 发布验收门禁 | **33 PASS / 0 FAIL / 2 HOLD** | 包装、依赖、隐私、结构与拒绝错误配置的门禁；不等于 33 次视频生成 |
| V29 生产必需测试 | **13/13** 工作流结构、**7/7** 发布范围、**17/17** 门禁修复 | 三组独立源码/契约测试均 PASS；**不是 37 次 GPU 测试** |
| 隔离安装/故障注入 | **9/9 PASS** | 依赖导入、配置及清晰报错；未生成视频 |
| 公开 Python / JS / JSON / PowerShell | **121 / 25 / 10 / 2** 个文件语法检查 PASS（该报告覆盖范围） | 文件语法有效，不等于全功能测试 |
| V28 历史全量兼容套件 | **ran=285；F=16 / E=56 / skipped=14** | **存在既有失败**，与当时发布候选基线一致、无新增；不能宣传 285/285 PASS |
| 工作流结构保护 | **181 节点 / 218 连线 / 2 子图**；冻结 Git Blob `aadee988ad2cce4d946e9054643a72f4d0e41d6b` | 发布前的唯一工作流保持不变 |

证据：[v29.4 FINAL_GATE_REPORT](acceptance/FINAL_GATE_REPORT.md)、[逐项 33 PASS / 2 HOLD JSON](acceptance/acceptance_v29_4.json)、[功能矩阵](FEATURE_MATRIX.md)、[发布说明](RELEASE_NOTES.md)。**旧报告里的候选分支“尚未 push/Release”是当时的时间点记录；v29.4 后来已正式发布，不能把旧报告当成当前 GitHub 发布状态。**

## 4. 仍然需要诚实展示的限制

1. **v29.4 公开源码整改没有重新完成全新机器、全链路六段 GPU E2E。** 历史 8197 成功不自动证明任何用户的新部署结果。
2. **2 个 v29.4 发布 HOLD**：语义性脱敏占位符、冻结 JSON 的参考图/历史元数据占位符；发布前报告另记录了 V28 全量旧测试失败、部分上游许可边界。参考图须用户自己指定。
3. **真实功能 vs 占位**：音频升级、V2V/RV2V、关键帧、Fun ControlNet、SLA、Progressive 等不可统一列入“全部 PASS”。
4. **模型/版权**：官方 MiniMax H3 提示词 Skill 原版不随包分发（`LICENSE_HOLD`）；外部 AudioRefine/ComfyUI/其他节点另装并遵守各自许可证。参阅 [上游归属](UPSTREAM_ATTRIBUTION.md)。
5. **8197 ≠ 8207**：8207 独立实验预览见 [H3-8207-Experimental](https://github.com/asd454314633-byte/H3-8207-Experimental)，不能将 8197 的 GPU 结果套用到 8207 公开候选。

## 5. 使用与验证入口

**先了解功能** → [工作流结构](ARCHITECTURE.md) · [22 项功能矩阵](FEATURE_MATRIX.md) · [原创贡献归属](../AUTHOR_CONTRIBUTIONS.md)。

**准备安装** → [Windows 安装指南（历史文件名含 8207，但仅用于 8197）](INSTALL_WINDOWS_8207.md) · [模型表](MODELS.md) · [v29.4 Release](https://github.com/asd454314633-byte/H3-Chinese-Director/releases/tag/v29.4)。

**看真实数据** → [六段耗时、峰值与合并](../benchmarks/SUMMARY.md) · [发布验收及已知 HOLD](acceptance/FINAL_GATE_REPORT.md)。
