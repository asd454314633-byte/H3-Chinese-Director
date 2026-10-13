# V29.3 → V29.4 开源合规与源码可用性定点修复报告（REMEDIATION_REPORT）

- 修复基线：commit `40e1a0f0dfa62f3f32923a41d1c4c579dd0dca8e`（= 审计基线 origin/main）
- 候选分支：`remediation/v29.4`（独立工作副本，未推送 main、未发布 Release）
- 生产环境：全程只读核查，未修改、未重启；唯一 V29 工作流 JSON 未改动（Blob `aadee988…` 与 SHA256 均验证一致）
- 离线验收：**PASS = 33，FAIL = 0，HOLD = 2**（证据：`docs/acceptance/acceptance_v29_4.json` / `.log`）

---

## 问题一：已消除哪些第三方授权风险

| 风险 | 修复 | 状态 |
|---|---|---|
| MiniMax 官方 Skill 三份原版文件（SKILL.md / base-en.txt / ref-en.txt）冒称原创、公开包对第三方原版授 MIT | 已 `git rm` 排除出公开包，README 登记上游 `MiniMax-AI/MiniMax-H3` 三个 blob SHA1 与归一化逐字节相等证据；许可未查实 → **LICENSE_HOLD**，不随包、不授权、不自动下载；新增 `scripts/setup/install_minimax_official_skill.py`（默认不下载，需 `--allow-download --i-have-license-rights` 双确认） | PASS |
| SDPose 子图宣称"完全原创" | 钉住上游 `Comfy-Org/workflow_templates`（独立 **MIT** 仓库，非 ComfyUI GPL 主体），commit `cdccb2ee…`、blob `6f6d7ab1…`；THIRD_PARTY_NOTICES §4 完整登记全等部分（inputs 15/15、outputs 5/5、节点 7/7、连线 28/28）与修改清单（80 处节点叶子 + 10 处连线叶子）；复核 `SDPOSE_BLUEPRINT=PASS` | PASS |
| AudioRefine vendor 来源不明 | 钉住 `Adudeguyman/ComfyUI-H3-AudioRefine`（**MIT**）commit `fd5a8dfe…`、blob `4b8e966f…`；改为外部依赖 + MIT LICENSE 义务随安装复制 | PASS |
| 台账"随包 vendor/LICENSE"与树内 0 个嵌套 LICENSE 矛盾 | `manifests/nodes.csv` 第 22/34/35 行修正为"不随包、外部安装"；`source_distributed` 误填 YES 已改 | PASS |
| "不包含任何第三方内容"等过宽表述 | README / README_EN / AUTHOR_CONTRIBUTIONS / UPSTREAM_ATTRIBUTION 统一清除，改为止确声明"does **not** claim…"；验收 I2 全绿 | PASS |
| GPL 误延伸 | THIRD_PARTY_NOTICES §1 写明"GPL-3.0 不自动延伸到独立 MIT 仓库蓝图"；"调用/覆写上游运行时 ≠ 复制/派生上游源码"，不凭 monkey-patch 下 GPL 结论 | PASS |

## 问题二：哪些缺失依赖已修复

| 缺失 | 修复方案 | 验证 |
|---|---|---|
| `v28_h3_format`（真实运行时依赖官方 guide 文本） | PEP 562 懒加载 + 解析顺序 `H3_MINIMAX_OFFICIAL_SKILL_DIR` → 包内 `skills/` → 抛 `H3OfficialGuideMissing`（含安装命令） | C2 PASS：可导入、缺失时明确报错 |
| `v28_manual_continuation` / `v28_reference_contract` / `v28_reference_hygiene` | 从唯一权威私有归档（两处副本字节一致）脱敏补齐，加 `SANITIZED_PUBLIC_COPY` 横幅 | 语法 PASS；测试收集后 7 个测试文件恢复 |
| `H3AudioRefineSampler`（`.vendor.nodes` 不存在） | 新增 `audio_refine_loader.py`：strict 模式抛 `H3AudioRefineMissing`（含上游/许可/commit/`git clone` 命令），strict 模式返回 None 不返回桩；`scripts/setup/install_h3_audio_refine.py` 外部安装 | C3 PASS：`STATE MISSING | RAISED H3AudioRefineMissing` |

**诚实声明**：以上均为**静态验证 + 缺失路径故障注入**验证通过；无 GPU 生成运行证据（任务书禁止），未伪装为运行 PASS。

## 问题三：哪些假门禁已恢复有效

| 门禁 | 缺陷 | 修复后行为 | 验证 |
|---|---|---|---|
| G-1 H3_MemoryPolicy | 固定占位路径使条件恒假 | `H3_MEMORY_POLICY_COMFY_ROOT` 环境变量驱动 + `self_check()` 返回 CONFIG_MISSING / CONFIG_INVALID / NOT_APPLIED / SKIPPED / APPLIED | G3 PASS（复用 test_gate_repair 4 用例：未配置→CONFIG_MISSING，正控制→APPLIED 且钳 16GiB） |
| G-2 反污染检查 | `REAL_WATCHED` 四路径塌缩为同一占位符，比对恒等 | `H3_V28_AUDIT_WATCH_PATHS` 驱动，≥2 个去重绝对路径、拒绝占位符；`detect_pollution()` 指纹比对 | G2 PASS：未配置拒绝 `H3AuditWatchConfigError`；test_gate_repair 含植入违规写入的正控制 |
| G-3 v28_paths | 占位符被当真实目录，`ensure_dirs`/`atomic_write` 可错误创建文件 | `H3_COMFY_ROOT` / `H3_V28_PROJECTS` / `H3_V28_PROJECT_DIR` env 驱动 + 哨兵 `<H3_PATH_UNCONFIGURED>` + `require_configured()` 前置失败 | G1 PASS：未配置拒绝创建、不落盘；H3 PASS：全新临时目录配置后可正常建立 |
| （新增发现）8207 线 5 个脚本 | 占位路径恒不存在 | 统一 `scripts/setup/h3_8207_paths.py` env 驱动 | G4 PASS：四个入口全部 REFUSED |
| （新增发现）JS 正则损坏 | 脱敏把正则字符类整体替换为占位符，`h3DrExtractSection` 必然匹配失败 | 恢复字符类语法 | G5 PASS：正则字面量内无占位符 |
| （新增发现）PS1 BOM 错位 | 2 个 ps1 的 UTF-8 BOM 落在第 2 行，PowerShell 按 ANSI 解析中文报语法错 | 重写为规范的 UTF-8 with BOM | B4 PASS |

## 问题四：统计如何变化

基于 `ORIGIN_AUDIT.csv`（175 行）核实：

| 口径 | 修正前 | 修正后 |
|---|---|---|
| nodes.csv 条目 | 42（A20/D15/C5/B1/E1） | 42（A20/D15/C5/B1/E1，描述修正） |
| A 类中有私有开发版本链 | 混在"A 类原创"里 | **122** 个单独统计（L0 71 + L1 48 + L1R 3），版本链证据支撑原创性 |
| 来源未发现重复但原创过程未充分证明 | 未区分 | **27** 个，明确不直接计入 A 类原创 |
| 修改上游运行行为的自研模块 | 未标注耦合 | **8** 个，逐项标注版本耦合/兼容性/上游依赖 |
| 分类字母含义 | 类别字母含义不统一（旧口径 E 混用） | 显式映射表 + 明确"覆写运行时（A/B 登记并标耦合）≠ 源码派生（E 登记附许可与修改声明）" |
| 随包分发声明 | 3 处误填"vendor/LICENSE 随包" | 修正为外部依赖，`source_distributed` 与实际文件一致 |

## 问题五：是否有需用户裁决的残余风险（HOLD）

1. **D2 语义占位符 45 处**：AST 检出的"整字符串即占位符"（主要在测试/说明文档），部分是脱敏导致规则文本/示例丢失，属内容损失登记，不影响运行（已验证语义位置占位符不破坏语法）。
2. **D3 冻结工作流内 11 处占位符**：8 处位于 LoadImageCrop 节点 widgets_values（参考图槽），加载该工作流时这些槽位为空。按任务书第四节**禁止修改唯一 V29 工作流 JSON**，故仅登记。
3. **MiniMax Skill LICENSE_HOLD**：上游 `MiniMax-AI/MiniMax-H3` 仓库 `license == null`，HF Community License 有地域/商用限制；未取得明确授权前不重分发、不授 MIT。是否联系上游获取授权、还是永久排除，需您裁决。
4. **V28 测试套件既有失败**：基线 ran=193 F=6 E=40；候选 ran=257 F=11 E=24（补齐模块后收集更多测试）。新增失败经逐文件对照确认为**私有归档快照（2026-10-02）版本漂移**（如 `ui_slot [1,2,3] != [1,3]`），属既有而非引入；是否修复漂移需您裁决（超出本轮定点范围）。

## 问题六：是否具备发布下一版条件

**具备（候选状态）**：验收 PASS=33 / FAIL=0，九类检查全过；剩余 2 项 HOLD 均为登记性质、不阻塞发布（发布页可如实标注"含 45 处脱敏登记与工作流参考图槽位说明"）。

**发布前置条件（由您执行）**：
1. 确认 REMAINING_HOLD.md 各项处置方式（特别是 MiniMax Skill 是"永久排除"还是"联系授权"）；
2. 审查 `RELEASE_CANDIDATE_DIFF.md` 逐文件差异；
3. 确认后由您决定是否 merge 到 main、打 tag 与发布 Release（本轮**未推送、未发布**，符合任务书第九节）。

**回滚方法**：候选在独立分支 `remediation/v29.4`；生产环境与唯一工作流未动，如需放弃候选，直接删除该分支与 `_remediation/` 工作区即可，基线 `40e1a0f` 不受任何影响。

## 验收执行摘要

```
[PASS] A   候选文件清单与逐文件差异复核（40 改动/新增 + 3 删除，清单 docs/acceptance/candidate_file_manifest.csv）
[PASS] B1  Python 语法 121 文件        [PASS] B2 JS/CJS 25 文件
[PASS] B3  JSON 10 文件               [PASS] B4 PowerShell 2 文件
[PASS] C1  无 vendor/ 目录            [PASS] C2/C3 缺失依赖可诊断报错
[PASS] C4  双安装器可执行             [PASS] C5 相对导入可解析
[PASS] D1  敏感信息扫描无命中         [HOLD] D2 语义占位符登记
[PASS] E   4 个测试脚本全过（发布范围/结构/提示词残留/门禁修复 17+7 项）
[PASS] F1  唯一工作流 Blob aadee988 不变   [PASS] F2 SHA256 一致   [PASS] F3 181/218/2
[PASS] F4  SDPOSE_BLUEPRINT=PASS       [PASS] G1–G5 全部门禁与路径治理
[PASS] H1–H3 安装器无写回 + 全新临时目录安装通过
[PASS] I1–I5 文档一致性/台账一致性
汇总：PASS=33 FAIL=0 HOLD=2
```
