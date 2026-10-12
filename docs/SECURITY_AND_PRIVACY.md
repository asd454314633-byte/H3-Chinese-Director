# 安全与隐私（SECURITY_AND_PRIVACY）

本仓库的每一份文件都经过**内容级脱敏**。本文说明：清洗了什么、保留了什么、没改什么、如何自检。

> **发布范围（最终收口）**：本仓库**只公开一套工作流** ——
> `workflows/current/V29_chinese_director_production_8197.json`（8197 冻结生产版）。
> 历代工作流（`workflows/history/`）、8207 实验工作流与历史工程档案（`history/`）已全部**退出公共发布**，
> 连同它们的历史文件清单与排除清单一起删除，只保留在作者本机生产归档中。
> 这样做的目的：历史 JSON / 日志 / 文本不可能被逐条无限期复核，**移出公开面**比"脱敏后再发"更可靠。

## 1. 清洗范围（内容级，非文件名级）

| 类别 | 处理方式 |
|---|---|
| 用户图片 / 视频 / 音频 / 参考素材 | 节点内图像二进制、base64、data URI、缩略图、预览缓存、图像元数据全部移除 |
| 素材文件名 | 文本与 JSON（含 dict 键）中的媒体文件名替换为 `<REDACTED_MEDIA>`；功能性哨兵 `__H3_GUIDE_NOT_SET__.png` 与 `example.png` 保留 |
| 个人创作提示词 | 六段剧情、角色设定、台词、正负提示词、续写缓存、测试输入全部清空或替换为统一中性文本 |
| 已填写的 REF2VA 结构化提示词 | 命中 `subject_definitions/summary/retention_analysis/detailed_description/...` 等 ≥2 个标记的，替换为**带占位符的中性官方模板** |
| 本机路径 | Windows 盘符路径（含源码字面量里的转义形式，形如 `<盘符>:\...` 或 `<盘符>:/...`）替换为 `<REDACTED_LOCAL_PATH>/<盘符>` |
| 用户家目录痕迹 | `Users\<name>\` 替换为 `<REDACTED_USER_HOME>` |
| 身份与凭据 | 邮箱、手机号（中文/电话语境判定）、私网 IP、GitHub/PAT、`sk-`、`AKIA`、JWT、`api_key/secret/password/token=...` 全部替换 |
| 运行状态与回执 | `six_prompt_state`、`h3_prebake_*`、`prompt_id`、`group_id`、`receipt`、`last_plan`、最新选图、UI 会话等恢复为代码定义的新用户默认态；示例清单里的真实 `prompt_id`/时间戳/进程号替换为 `<REDACTED_RUNTIME_ID>` / `<REDACTED_TIMESTAMP>` / `null` |
| 浏览器数据 | Chrome/Edge profile、扩展源码、Local Storage / IndexedDB / Service Worker 等目录**整体排除**，不进入仓库 |
| 未知二进制 | 无法确认可安全解析的二进制一律不公开（历史上记入 `manifests/exclusions.csv`；该清单随历史档案一起退出公开包） |
| 历史档案 | `workflows/history/`、`history/`、`manifests/public_files.csv`、`manifests/exclusions*.csv` **整目录删除**，不再作为"脱敏副本"发布 |

## 2. 明确保留

- 节点类型、连线拓扑、参数名、经验证的通用默认值（**不为脱敏破坏工作流**）
- 真正属于功能逻辑的通用系统模板、字段模式与编译规则（如带 `<Picture 1>` 占位符的官方 REF2VA 模板骨架）
- 上游公开 URL（GitHub / HuggingFace / 官方文档）、软件版本号、`127.0.0.1` 示例
- 工作流中的说明性 `Note` / `MarkdownNote`（其中若有私有路径或素材名，也已逐条清洗）
- 第三方节点来源台账 `manifests/nodes.csv`（归属与许可需要长期可追溯，不随历史档案删除）

## 3. 明确**未**篡改

- 真实耗时、日期、错误原因、PASS / PARTIAL / HOLD / NOT_TESTED 结论（`benchmarks/`）
- 历史失败与 HOLD 结论（**不挑最快成绩当统一结论**）
- 被删除的档案里的数字**保持原样引用**，只在 `evidence_file` 列改用 `LOCAL_ARCHIVE:` 前缀标明"出处在生产侧本机归档"，不因此删改任何一次实测值

## 4. 标记

每份由私有原件生成的公开文件首行带有：

```
SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
```

私有原始 → 公开替代的逐文件映射表**只保留在本机**，不随公开仓库发布（公开侧不再有 `manifests/public_files.csv`）。

## 5. 发布前闸门（全部通过才推送）

| 闸门 | 内容 | 本仓库现状 |
|---|---|---|
| A. SANITIZE_WORKFLOW | 唯一公开工作流无个人素材/提示词/路径/身份/运行状态 | 逐节点审计 0 命中，见 §6 与 `tests/` |
| B. SANITIZE_ARCHIVES | 历史报告/日志/脚本同标准；未知二进制零放行 | **改判为"不公开"**：档案整体撤出，不再依赖逐条脱敏 |
| C. SECRET_SCAN | 全树凭据/身份扫描，命中零放行 | `scripts/sanitize/scan_sensitive.py` 零命中 |
| D. PROVENANCE_LICENSE | 每项来源、作者、修改权、许可可追溯 | `manifests/nodes.csv` + `docs/UPSTREAM_ATTRIBUTION.md` |
| E. REPRODUCIBILITY | 可部署、可加载、可跑无需模型的测试 | `scripts/verify/` + `tests/` 全绿 |
| F. HISTORY_TRACEABILITY | 计数、清洗/排除/去重映射、测试证据完整，无静默丢件 | **改判为"公开侧无历史档案"**：本机保留完整 bundle 恢复点 |
| G. FROZEN_SOURCE_UNCHANGED | 私有源 SHA256 复核未变 | 冻结生产原件只读，未改动 |
| H. PUBLIC_STAGING_REVIEW | 人工抽查 + `git ls-files` 全量核对 | 全新目录克隆复核，见 `docs/RELEASE_NOTES.md` |

## 6. 唯一 V29 工作流的逐节点隐私审计

审计对象：`workflows/current/V29_chinese_director_production_8197.json`（Git blob SHA
`aadee988ad2cce4d946e9054643a72f4d0e41d6b`，blob 字节 SHA256 `311609b1e03316e724b97c8cf8783451955cb22a12fd3ea31844e6632488302e`）。
覆盖范围：181 个顶层节点 + 2 个内嵌子图（`definitions.subgraphs`）内 15 个节点，含 `nodes/links/groups/definitions/widgets_values/properties/extra` 的全部 15,911 条字符串叶子。

| 断言项 | 结果 |
|---|---|
| 用户图片 / 内嵌私有图像 / base64 / data URI | **0** |
| 正向 / 负向提示词中的私人剧情 | **0** |
| 六段导演文字（`six_prompt_state.texts`、`h3_prebake_texts`、`h3_six_prompts`） | **全空** |
| 私人路径 / 素材文件名 / 身份 / 凭据 | **0** |
| 运行回执（`story_id`、`bake_receipts`、`last_plan`、`revisions`） | 空串 / `null` / `[0,0,0,0,0,0]` |
| 未定义（无法解析）节点类型 | **0** |
| 节点与连线结构 | 与生产原件逐项对拍：**同拓扑**（连线表逐字节一致；差异只出现在被替换的文本值上） |
| 公开版 Blob SHA | 与冻结值一致，脱敏未改动结构 |

## 7. 你可以自行复核

```bat
:: 1) 结构门禁（无需模型）
python scripts/verify/verify_workflow_structure.py

:: 2) 全树敏感项扫描（复用与发布时同一套规则）
python scripts/sanitize/scan_sensitive.py <repo_root>

:: 3) 发布范围与隐私契约断言（唯一工作流 / 历史目录缺席 / 无个人提示词 / 无内嵌图片）
python tests/test_workflow_structure.py
python tests/test_public_release_scope.py
python tests/test_no_personal_prompt_residue.py
```

脚本规则与发布时完全一致，命中即为 0 才算通过。

## 8. 如果你发现了泄漏

请通过 issue 说明**文件路径 + 行号 + 命中类型**。维护者按「先下架、后修正」处理：先把该文件从仓库移除，
再重新脱敏后以新 commit 恢复，并在需要时用 `git filter-repo` 重写历史 + 重发 Release。

## 9. 历史残留与外部副本（诚实声明）

- 本仓库先后使用过 `git filter-repo` 历史重写与**孤儿提交全新历史**。force-push 之后，旧 commit 在 GitHub
  上会短时间内**仍可按完整 SHA 直接访问**，并且已删除的 Release 附件、fork、CDN 缓存与搜索引擎快照都可能留有旧字节。
- 因此本仓库**不宣称**"外部副本已彻底消失"。需要在 GitHub 之外收敛的部分（旧 commit 可达性、旧 Release/附件缓存、
  可能存在的 fork）会逐项登记在 `docs/RELEASE_NOTES.md` 的「待 GitHub Support 清理对象」表中，并另行提交清理请求。
- 判定"删除完成"的口径是：**在当前 main 的历史、当前标签与当前 Release 附件中，被撤回的内容不可达**；
  而不是"互联网上任何角落都不再存在"。

## 10. v29.2 补丁：个人创作提示词残留修复（2026-10-12）

外部复审发现 1 处、自查扩展确认为 **5 个签名 / 14 个历史工作流文件 / 24 处字符串**的个人创作提示词残留
（具体人物、姿势、参考图分工、身份替换约束、AI 伴侣闲置镜头等具体创作指令）。

**根因**：此前的内容脱敏规则针对中文对白格式（`<d>[Chinese]...`）构建，英文长创作提示词不在检测范围。

**处置（当时的口径）**：
- 24 处字符串全部替换为 `<REDACTED_PERSONAL_PROMPT>`（与仓库既有 `<REDACTED_*>` 占位符约定一致）。
- 判定标准（公开可复核）：长度 ≥500 字符 + 创作词汇/描述符堆叠/负向提示词特征，且**不含**通用模板占位符
  （`<Subject N>` / `<Picture N>` 等）。含占位符的参数化模板（导演台 subject_definitions 机制）与节点功能文档
  **不属于**个人创作提示词，予以保留。
- 回归测试 `tests/test_no_personal_prompt_residue.py` 已加入测试套件：已知 5 签名永久断言 + 规则扫描。

**最终处置（v29.3 收口）**：上述 14 个历史工作流文件连同整个 `workflows/history/`、`history/` 一起**退出公开包**——
不再依赖"脱敏后的历史副本"，个人创作内容的公开面收敛为**唯一 V29 工作流 + 自研源码 + 文档**。
残留签名断言与规则扫描**继续保留**在测试里，作为对现存公开文件的永久回归门禁。
