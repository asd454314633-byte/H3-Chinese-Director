# RELEASE_NOTES — H3 Chinese Director（V29 唯一冻结生产工作流）

> 本文件随仓库发布。对应的本地验收报告（含完整闸门证据与私有映射）留在私有工作区，不公开。

## 状态

**FINAL_SINGLE_V29_PUBLISHED**（2026-10-12 收口发布）。

| 完成条件键 | 结果 |
|---|---|
| `SINGLE_V29_WORKFLOW` | **PASS** — 公开包内只有 `workflows/current/V29_chinese_director_production_8197.json` |
| `PUBLIC_HISTORY_REMOVAL` | **PASS** — `workflows/history/`、`history/`、历史清单与排除清单已全部退出公开包 |
| `WORKFLOW_PRIVACY_AUDIT` | **PASS** — 逐节点（181 顶层 + 子图 15）隐私审计，见 `docs/SECURITY_AND_PRIVACY.md` 第 6 节 |
| `SOURCE_CODE_PRESERVED` | **PASS** — 8197 冻结生产线自研节点/前端/运行接口/安装工具/许可/模型来源/二次开发文档完整保留（8207 实验线镜像源码已整体排除，不为唯一工作流所需） |
| `FRESH_CLONE_VERIFY` | **PASS** — 空目录全新克隆复核（文件数、逐文件 SHA256、结构门禁、敏感扫描、历史不可达） |

- 仓库：<https://github.com/asd454314633-byte/H3-Chinese-Director>（Public）
- 唯一公开工作流：`workflows/current/V29_chinese_director_production_8197.json`
  - Git blob SHA：`aadee988ad2cce4d946e9054643a72f4d0e41d6b`
  - blob 字节 SHA256：`311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`
- 发布提交 / Release 与附件哈希：见文末「本次发布坐标」（推送后回填，与远端一致）

## 本次发布范围（唯一 V29 收口）

**公开**：

- **1 套工作流**：`workflows/current/V29_chinese_director_production_8197.json`（8197 冻结生产版，含六段中文导演台默认态）
- **本地作者自研节点源码与前端**（`custom_nodes/local_author/8197_production_line/`，8197 冻结生产线；8207 实验线源码不在公开包内）：中文导演 UI、六段状态机、PreBake conditioning 缓存、原生接续、自适应 Host Warm、选择性 TE 卸载、手动链式合并、V28 导演编排等
- **安装 / 验证 / 脱敏工具**（`scripts/setup|verify|sanitize/`）
- **许可与归属**（`LICENSE`、`THIRD_PARTY_NOTICES.md`、`docs/UPSTREAM_ATTRIBUTION.md`、`manifests/nodes.csv`）
- **模型来源说明**（`docs/MODELS.md`，不含权重）与**二次开发文档**（`docs/ARCHITECTURE.md`、`docs/FEATURE_MATRIX.md`、`docs/INSTALL_WINDOWS_8207.md`、`docs/SECURITY_AND_PRIVACY.md`）
- **结构性测试**（`tests/`、`scripts/verify/verify_workflow_structure.py`）与非工作流合成夹具（`fixtures/synthetic/`）
- **基准数据**（`benchmarks/`）：**120 条**实测指标（六段生成耗时、自动合并、显存/RAM 峰值等），来源文件与行号可追溯；`evidence_file` 列以 `LOCAL_ARCHIVE:` 前缀指向生产侧本机归档

**不再公开**（全部退出公共发布，只保留在作者本机生产归档）：

- `workflows/history/` —— 历代工作流（v29.2 时为 191 份）
- `workflows/current/` 内的其余 5 份（8207 实验工作流 3 份 + 8207 UI 候选 + PreBake 候选）
- `history/` —— 历史报告 / 变更台账 / 决策记录 / 维修记录（v29.2 时为 6,335 份）
- `manifests/public_files.csv`、`manifests/exclusions.csv`、`manifests/exclusions_summary.csv` —— 随历史档案失效
- `fixtures/synthetic/synthetic_min_director_workflow.json` —— 该夹具本身是**一套可导入工作流**，按"只发布一套工作流"的口径移出公开包（测试改为直接断言唯一生产工作流的对应契约，不再依赖它）
- `custom_nodes/local_author/8207_line/` —— 8207 实验线镜像源码（139 个文件：130 个与 8197 生产线逐字节相同、8 个为独立演进版、1 个为 8207 线专用垫片）。经依赖审计，唯一 V29 工作流与必要安装工具**均不依赖**该目录，故整体排除；安装文档中指向它的命令已一并移除

## 脱敏声明

全部内容经内容级脱敏：个人素材/媒体、个人创作提示词、本机路径与身份、凭据、运行状态与运行回执已清除；
结论性数据（耗时、日期、错误原因、PASS/HOLD 判定）**未篡改**。
已知豁免（无身份信息的技术残留）逐项记录于 `docs/SECURITY_AND_PRIVACY.md`。

## 验证

- 源码可用性 `scripts/verify/verify_source_usability.py`：**SOURCE_USABILITY=PASS**（PY / JSON / JS / PS1 / TOKEN / PKG 全部可解析、可导入、语法有效）
- 敏感项自检 `scripts/sanitize/scan_sensitive.py`：**零命中 PASS**（全树文本文件）
- 结构门禁 `scripts/verify/verify_workflow_structure.py`：**唯一公开工作流通过**
- 逐节点隐私审计：内嵌图片 0 / 个人提示词 0 / 六段文字全空 / 私人路径 0 / 身份 0 / 运行回执空 / 未定义节点 0
- 结构对拍：连线表逐字节一致，节点类型/mode/pos/size/端口连接逐项一致，**差异只在被替换的文本值**；Blob SHA 与冻结值相同
- 契约测试（全部实跑通过）：
  - `tests/test_public_release_scope.py` → `PUBLIC_WORKFLOW_COUNT = 1`、`PUBLIC_WORKFLOW = workflows/current/V29_chinese_director_production_8197.json`、`HISTORY_DIRECTORY = ABSENT`、`PERSONAL_PROMPT_RESIDUE = 0`、`EMBEDDED_PRIVATE_IMAGE = 0`
  - `tests/test_workflow_structure.py` → `STRUCTURAL_REGRESSION=PASS`（13/13）
  - `tests/test_no_personal_prompt_residue.py` → `PERSONAL_PROMPT_RESIDUE=0`（判定尺经植入样本自证有效，未放宽）
- 依赖审计：唯一工作流 34 个 `H3*` 节点类型中 27 个解析到 `8197_production_line` 源码、7 个由工作流元数据归属第三方节点包（`comfyui-mainodes` 等，按安装文档单独安装）、**0 个未解析**；`8207_line` 目录不为其中任何一类提供实现

## 未包含

模型权重、第三方节点源码、浏览器数据、压缩包、无法解析的二进制、历代工作流与历史工程档案。
模型从 `docs/MODELS.md` 列出的官方来源自行下载。

## 版本补丁记录

### v29.3（2026-10-12）— 唯一 V29 收口 + 全新 Git 历史

- 公开面收敛为**唯一 V29 冻结生产工作流**；`workflows/history/`、`history/`、历史清单与合成工作流夹具全部移除。
- 用**孤儿提交建立全新单一提交历史**（非在原历史上追加删除提交）：旧工作流与历史档案不经任何父提交可达。
- 撤回 v29.2 Release 及其全部附件（含历史归档 zip），不再提供可直接下载的旧 ZIP。
- 文档口径同步：删除"197 份工作流 / 6,335 份历史档案 / 6,716 文件"等旧数字，改为唯一工作流口径。
- 新增 `tests/test_public_release_scope.py` 发布范围契约测试；既有提示词残留回归测试改为作用于全部公开 JSON 文件。
- **8207 实验线镜像源码整体排除**（`custom_nodes/local_author/8207_line/`）：依赖审计确认唯一 V29 工作流与必要安装工具均不依赖它；安装文档、README、架构文档、贡献清单与 `manifests/nodes.csv` 中指向它的引用全部修正，不留下失效的安装步骤；提示词残留判据未放宽（镜像删除后 `PERSONAL_PROMPT_RESIDUE=0` 为真实通过）。
- 另修正一处运行回执外露：`scripts/verify/8207_acceptance_report.py` 中的真实 `prompt_id` 已替换为 `<REDACTED_RUNTIME_ID>`（与仓库脱敏契约一致）。

### v29.2（2026-10-12）— 个人创作提示词残留修复

外部复审发现 1 份历史工作流残留完整个人创作提示词；自查扩展确认共 5 个签名、14 个历史工作流文件、
24 处字符串。已全部替换为 `<REDACTED_PERSONAL_PROMPT>`，根因（脱敏规则未覆盖英文长创作提示词）已记录于
`docs/SECURITY_AND_PRIVACY.md`。v29.3 起这 14 份文件随整个历史目录退出公开包。

### v29.1（2026-10-12）— 文档修正

KJNodes 许可更正（MIT→GPL-3.0，经 GitHub API 核实）、第三方节点提交锁定表、
Windows Git 客户端预配置（longpaths / autocrlf）、安装指南 cd 路径自包含化。

### v29（2026-10-12）— 首次发布

首个公开快照（当时包含 197 份工作流与 6,335 份历史档案）；已由 v29.3 的全新历史与撤回附件取代。

## 待 GitHub Support 清理对象（诚实声明）

force-push 与 Release 删除**不等于**外部副本消失。以下对象在删除动作之后仍可能在一段时间内被直接命中，
需通过 GitHub Support / 官方渠道逐项请求清理；本仓库不宣称它们已经彻底不存在：

| 类型 | 对象 | 说明 |
|---|---|---|
| 旧提交（按 SHA 直接访问） | `2e2542ca0d759fbfee9d9c66390cea7ff1d37c39` | v29 首版；含当时的 197 份工作流与 6,335 份历史档案 |
| 旧提交（按 SHA 直接访问） | `7756374`（v29.1）、`9145c27`（v29.2 前） | v29.1 文档补丁 / 被 filter-repo 重写前的提交 |
| 旧提交（filter-repo 重写产物） | `0cbe3d1`、`a4f3896`、`ae85f75` | v29.2 重写后的三个提交，v29.3 全新历史后即不可达 |
| 旧标签 | `v29`、`v29.2` | 已删除；Git 服务端标签缓存可能短时残留 |
| 旧 Release 与附件 | `v29`（source-full.zip 50.0 MB / history-archive.zip 42.5 MB / SHA256SUMS）、`v29.2`（source-full.zip 49.99 MB / history-archive.zip 42.48 MB / SHA256SUMS） | 已删除；Release 资产 CDN 缓存与已完成的下载链接需官方侧清理 |
| 派生副本 | 任何 fork、GitHub 搜索索引、第三方镜像 / 搜索引擎快照 | 上线至今未见 fork 迹象；索引侧清除需官方执行 |

## 本次发布坐标

（推送完成后由发布脚本回填，与远端实际值逐字一致。）
