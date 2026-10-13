# RELEASE_NOTES — H3 Chinese Director（V29 唯一冻结生产工作流）

> 本文件随仓库发布。对应的本地验收报告（含完整闸门证据与私有映射）留在私有工作区，不公开。

## 当前公开版本与维护说明

- **最新已发布 Release：** [v29.4](https://github.com/asd454314633-byte/H3-Chinese-Director/releases/tag/v29.4)（开源合规与源码可用性修复版）。
- **唯一工作流**始终取自 Git Blob `aadee988ad2cce4d946e9054643a72f4d0e41d6b`，原始字节 SHA256 为 `311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`。
- v29.4 Release 的独立 JSON 和源码归档已经完成 LF 字节一致性修复；早期发布说明中的 `b11a9698...` 为修复前 CRLF 附件的旧摘要，**不再用于校验**。
- 后续维护仓库只更新安装说明、链接和自动化门禁，**不更改** V29 工作流或 v29.4 标签；下文 v29.3 的文件数、快照提交与“本次发布坐标”属于**历史 v29.3 记录**，不是当前主分支的文件统计。
- 既有 V29 生产 GPU 验收继续有效；v29.4 源码修复的 GPU 端到端测试未重新执行，不能混淆验收范围。

## v29.3 历史收口状态（非当前 main 提交数）

**FINAL_SINGLE_V29_PUBLISHED**（2026-10-12 收口发布）。

| 完成条件键 | 结果 |
|---|---|
| `SINGLE_V29_WORKFLOW` | **PASS** — 公开包内只有 `workflows/current/V29_chinese_director_production_8197.json` |
| `PUBLIC_HISTORY_REMOVAL` | **PASS** — `workflows/history/`、`history/`、历史清单与排除清单、8207 实验线镜像源码已全部退出公开树；全新 Git 历史仅 1 个无父提交，旧内容不经任何父提交可达（旧提交 SHA 在官方对象库清理前仍可直接访问，见文末诚实声明，**不宣称"完全删除"**） |
| `WORKFLOW_PRIVACY_AUDIT` | **PASS** — 逐节点（181 顶层 + 子图 15）隐私审计，见 `docs/SECURITY_AND_PRIVACY.md` 第 6 节 |
| `SOURCE_CODE_PRESERVED` | **PASS** — 8197 冻结生产线自研节点/前端/运行接口/安装工具/许可/模型来源/二次开发文档完整保留（8207 实验线镜像源码已整体排除，不为唯一工作流所需） |
| `FRESH_CLONE_VERIFY` | **PASS** — 空目录全新克隆复核（文件数、逐文件 SHA256、结构门禁、敏感扫描、历史不可达） |

- 仓库：<https://github.com/asd454314633-byte/H3-Chinese-Director>（Public）
- 唯一公开工作流：`workflows/current/V29_chinese_director_production_8197.json`
  - Git blob SHA：`aadee988ad2cce4d946e9054643a72f4d0e41d6b`
  - blob 字节 SHA256：`311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`
- 发布提交 / Release 与附件哈希：见文末「本次发布坐标」（推送后回填，与远端一致）

## v29.3 历史发布范围（唯一 V29 收口）

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

### v29.3 补丁（2026-10-12）— Support 清理请求登记

- 按 GitHub 官方流程提交 Support 清理工单 **#4849129**（`rr-remove-sensitive-data`），申请对 8 个仍可按 SHA 直接访问的旧提交执行服务端 GC、清除 cached views 与已删除 Release 附件的 CDN 缓存；文末「待 GitHub Support 清理对象」表已同步登记该工单号与剩余风险。**在 Support 完成清理前，本仓库持续标记该风险，不宣称已彻底清除。**

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
需通过 GitHub Support / 官方渠道逐项请求清理；本仓库不宣称它们已经彻底不存在。

v29.3 收口时的**实测可达性**（2026-10-12，匿名复查）：

| 类型 | 对象 | 删除动作 | 匿名复查结果 |
|---|---|---|---|
| 旧 Release 页面 | `v29`、`v29.2` | 已删除（id 410437542，含 3 个附件） | **404（不可达）** |
| 旧标签 | `v29.2` | 已删除 | 已不存在（`tags` 列表为空 → 仅剩 `v29.3`） |
| 旧提交（按 SHA 直接访问） | `d19d35e`、`b3d3562`、`ae85f75`、`a4f3896`、`0cbe3d1`、`9145c27`、`2e2542c`、`7756374` | 失去全部引用（孤儿提交强推后不在 main 历史中） | **仍返回 200（可按 SHA 直接访问）→ 必须向 GitHub Support 申请清理** |
| 旧 Release 附件 CDN 缓存 | `v29` / `v29.2` 的 source-full.zip、history-archive.zip | 已删除 | 下载链接失效，CDN 缓存需官方侧清理 |
| 派生副本 | 任何 fork、GitHub 搜索索引、第三方镜像 / 搜索引擎快照 | — | 上线至今未见 fork 迹象；索引侧清除需官方执行 |

**结论**：不得宣称"完全删除"。当前 main 历史（仅 `ee632c7f` 一个无父提交）、当前标签（仅 `v29.3`）与
当前 Release 附件中，被撤回的内容**不可达**；但上述旧提交 SHA 在官方对象库清理前仍可直接访问。

**Support 清理请求已提交（2026-10-12）**：按 GitHub 官方流程
（<https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository>
→ GitHub Support 联系表单，标签 `rr-remove-sensitive-data`）已创建工单
**#4849129**（<https://help.github.com/ticket/personal/0/4849129>，状态 Open，优先级低），
内容包含：仓库名、受影响 PR 数（0，实测无 PR / 无 fork）、待清理的 8 个旧提交完整 SHA、
敏感内容性质说明（个人创作提示词残留 + 误纳入的 6,335 份历史档案，非可轮换凭据）、
以及已完成的清理动作（孤儿提交强推 / 旧 Release 与标签删除）。同时申请清除旧提交 URL 的
cached views 与已删除 Release 附件的 CDN 缓存。

**剩余风险（在 Support 完成清理前持续有效）**：上表 8 个旧提交 SHA 实测仍返回 200；
工单处理时长与结果由 GitHub 决定，本仓库持续标记该风险，**不宣称已彻底清除**。

## v29.3 历史发布坐标

- 仓库：<https://github.com/asd454314633-byte/H3-Chinese-Director>（Public）
- 发布提交（孤儿提交，无父提交）：`ee632c7f2808628d28b589da17d5f4e65c44c226`
- Release：`v29.3` — <https://github.com/asd454314633-byte/H3-Chinese-Director/releases/tag/v29.3>
  - 附件：`H3-Chinese-Director-v29.3-source.zip`（清洁源码包，git archive of `ee632c7f`）、
    `V29_chinese_director_production_8197.json`（唯一工作流）、`RELEASE_SHA256SUMS.txt`
  - source.zip SHA256：`0f1fd15ec30105ab68aa46fcd9f92620817327b892025a93be7f7745ae1859cc`
  - 工作流 JSON SHA256：`311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`
- 公开文件总数：175（`.py` 111 / `.js` 21 / `.md` 18 / `.json` 9 / `.cjs` 4 / `.txt` 3 / `.yaml` 2 / `.ps1` 2 / `.csv` 2 / `.ini` 1 / `.gitignore` 1 / `LICENSE` 1 —— 以 `git ls-files` 实测为准）
- 唯一工作流：`workflows/current/V29_chinese_director_production_8197.json`
  - Git blob SHA：`aadee988ad2cce4d946e9054643a72f4d0e41d6b`
  - blob 字节 SHA256：`311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`
- 全新克隆复核：空目录克隆后 `git rev-list --count HEAD = 1`（无父提交）、175 文件、唯一工作流 Blob 不变、
  全部门禁（源码可用性 / 结构 / 敏感扫描 / 残留 / 范围契约）复跑通过
- 恢复点（仅本机，不上传）：`h3_publish/_private/pre_rewrite_mirror_20261012_full/`（强推前远端完整镜像克隆）、
  `h3_publish/_private/pre_rewrite_backup_20261012.bundle`（更早的 bundle）、
  `h3_publish/_private/excluded_8207_line_20261012/`（被排除的 8207 镜像源码副本）
