# 功能矩阵与验收状态（FEATURE_MATRIX）

> **公开范围**：本仓库只发布 8197 冻结生产线。下表「8207 线」列仅用于登记**验收边界**（防止把 8197 的
> PASS 误当作 8207 的 PASS）；8207 线源码不在公开包内，安装本仓库**不需要**该列对应的任何组件。

状态定义：

- `PASS` —— 有真实验收（真实生成 / 真实回归 / 真实浏览器）记录
- `PASS_WITHIN_TESTED_SCOPE` —— 通过，但仅限已测范围，不推广到未知人物/镜头
- `PARTIAL` —— 单项通过但整体链路未验收
- `NOT_TESTED` —— 未验收（不谎称 PASS）
- `HOLD` —— 有结论但被门控挂起
- `DECLARED_ARCHITECTURE_ONLY` —— 仅登记架构位置，无可执行实现

| # | 功能 | 归属 | 8197 冻结线 | 8207 线 | 证据 |
|---|---|---|---|---|---|
| 1 | 全中文集中控制导演台（单入口） | A 自研 | PASS | PASS（UI 线） | 181/218 节点 fresh load；82 节点干跑 required-input errors=0 |
| 2 | 六段剧情编辑与状态管理 | A 自研 | PASS | PARTIAL | 六段真实 SUCCESS；崩溃恢复测试 PASS |
| 3 | 连续视频生成调度 | A 自研 | PASS | NOT_TESTED | 18 项 DOM/mock 回归 + 真实 HTTP200 |
| 4 | 上一段 AV Latent 接续 | C 编排 | PASS | NOT_TESTED | SEG2 续接 SEG1 latent，H3 重读 0 字节 |
| 5 | Conditioning PreBake 缓存 | A 自研 | PASS | PARTIAL | 离线回归 26 项 PASS |
| 6 | PreBake 失效与恢复 | A 自研 | PASS | NOT_TESTED | 改段文字→后续回执失效；中断后从第 4 段恢复 |
| 7 | 自动六段视频合并 | A 自研 | PASS | NOT_TESTED | 合并 41.5s / 996 帧；5 接缝一致 |
| 8 | 工作流安全门控与回执校验 | A 自研 | PASS | NOT_TESTED | 旧回执拒绝 PASS；cache 缺失 HTTP409 拦截 |
| 9 | Adaptive Host Warm（pre-TE release） | B 二次开发 | PASS | NOT_TESTED | 三条真实路径验收通过并晋升 |
| 10 | TE selective unload | B 二次开发 | PASS | NOT_TESTED | 生产晋升记录 |
| 11 | PDD 308 patch 兼容（回退父 patcher） | B 二次开发 | PASS | NOT_TESTED | Node136 生命周期冲突修复 |
| 12 | VAE 前 partial eviction | B 二次开发 | PASS | NOT_TESTED | 生产晋升记录 |
| 13 | 五路注意力路线切换 | C 编排 | PASS_WITHIN_TESTED_SCOPE | NOT_TESTED | 五路分列；SLA / BlockSparse 仅登记架构 |
| 14 | Ref2VA 多参考（图/视频/音频） | C 编排 | PASS_WITHIN_TESTED_SCOPE | NOT_TESTED | 真实多参考生成 |
| 15 | 视频重绘 V2V / RV2V | C 编排 | PARTIAL（架构位已接线，默认旁路） | NOT_TESTED | 画布保留执行体并旁路 |
| 16 | 关键帧时间线（Guide Timeline） | A 自研 | NOT_TESTED（8197 未启用） | PARTIAL | 8207 候选存在，未 GPU 验收 |
| 17 | Fun ControlNet（Union 2.0） | C 编排 | NOT_TESTED | PARTIAL | 8207 候选 |
| 18 | 高分辨率增强（Progressive / SelfLift） | — | DECLARED_ARCHITECTURE_ONLY | — | 仅占位，明确不手搓 |
| 19 | SLA 混合线性稀疏 | — | DECLARED_ARCHITECTURE_ONLY | — | 不迁移、不安装、不伪造可运行 |
| 20 | 音频 8 步 / 音频升级 | A 自研 | PARTIAL | NOT_TESTED | 可选分支，非主验收范围 |
| 21 | 前端开关持久化（tab 切换双态保持） | A 自研 | PASS（1.52.7 实测） | — | `TAB_SWITCH_MODE_PERSISTENCE = PASS` |
| 22 | GUIDE 权威归一 | A 自研 | PASS | 不适用（8207 冻结件不含该补丁） | helper sync 无法翻转 GUIDE OFF |

## 明确未验收 / 不做的事

- **不宣称**内存无忧：`MEMORY_MARGIN = LIMITED`，热路径 Commit 峰值约 90.2%（采样峰值记录 95.05 GiB）。
- **不宣称**「所有人物/镜头通用」：视觉连续性结论为 `PASS_WITHIN_TESTED_SCOPE`，不推广到未测人物与机位。
- **不把** 8197 的 PASS 当作 8207 的 PASS：8207 线除 UI 线外大多为 `NOT_TESTED` / `PARTIAL`。
- **不提供** SLA、Progressive/SelfLift 的可执行实现，只登记架构位置。

## 复现方式

- 结构性（无需模型）：`python scripts/verify/verify_workflow_structure.py`
- 需模型的功能项：导入工作流并按 `docs/INSTALL_WINDOWS_8207.md` 部署后自行验收；本仓库不代跑 GPU 压力测试。
