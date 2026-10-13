# REMAINING_HOLD — 残余未决事项（不做无依据法律定论，不伪装 PASS）

以下事项按任务书要求**如实登记为 HOLD**，不属于本轮 PASS 范围，需用户裁决后处置。

## HOLD-1 ｜ MiniMax 官方 Skill 许可（LICENSE_HOLD）【需裁决：高优先级】

- 上游 `MiniMax-AI/MiniMax-H3` 仓库 **`license == null`**（GitHub API 核实），Hugging Face Community License Agreement 存在地域/商用限制。
- 三份官方原版文件已从公开包排除（blob SHA1 `b6d9b283` / `40cf586a` / `7ae1b2d0` 逐字节比对留档），移除前 SHA256 已留档。
- 运行时 `v28_h3_format.py` 依赖该 guide 文本：已实现外部安装（env `H3_MINIMAX_OFFICIAL_SKILL_DIR` 或包内 `skills/`），缺失时抛 `H3OfficialGuideMissing` 并附安装命令；安装器默认不下载，需 `--allow-download --i-have-license-rights` 双确认。
- **未决**：是否联系上游取得明确授权（永久排除 vs 获权后恢复引用）。未取得授权前：不重分发、不授 MIT、不自动下载。

## HOLD-2 ｜ 冻结工作流内的占位符（11 处）【禁止修改，仅登记】

- 唯一 V29 工作流 JSON 内含 11 处 `<REDACTED_*>` 占位符，其中 **8 处位于 LoadImageCrop 节点的 widgets_values（参考图槽）**——即这些槽位本就是"每用户本地参考图"，占位符表示"待用户装载"，加载工作流不会因占位符崩溃，但参考图需用户自行指定。
- 其余 3 处为文本域占位（脱敏自历史用户提示词）。
- 任务书第四节**禁止修改该 JSON**，故仅登记。发布页建议附一句说明："工作流中带 <REDACTED_*> 的槽位需用户装载自己的参考图/提示词"。

## HOLD-3 ｜ 语义位置占位符（约 45 处）【内容损失登记】

- `verify_source_usability.py` 新增的 AST 语义检查发现约 45 处"整字符串即占位符"，主要分布在测试文件与说明文档（director_engine 1、v28_director_core 2、v28_mock_provider 3、v28_orchestrator 2、v28_routes 1 等）。
- 性质：脱敏把"规则文本/示例正文"整体替换为占位符，属**内容损失**；已验证不破坏语法与运行（B1/B2/B5 PASS）。`director_rules.py` 的规则文本损失已通过 `REDACTED_RULE_SLOTS` 显式登记。
- **未决**：是否在后续版本用"非个人创作的合成示例"回填这些槽位（涉及新的创作判断，超出本轮定点修复范围）。

## HOLD-4 ｜ V28 测试套件既有失败（私有归档版本漂移）【需裁决：是否修复】

- 基线（repo HEAD）：ran=193，F=6，E=40；候选：ran=257，F=11，E=24（补齐 4 模块后收集到更多测试）。
- 逐文件对照确认新增失败集中在恢复模块相关测试，根因是**私有归档快照（2026-10-02）与 HEAD 的版本漂移**（例：`ui_slot [1,2,3] != [1,3]`、`Picture 2 vs Picture 3`、`OFFICIAL_H3_FORMAT_INVALID` 未抛），属**既有漂移而非本轮引入**。
- 设置 `H3_MINIMAX_OFFICIAL_SKILL_DIR` 后 E 从 34 降至 24。
- **未决**：是否安排后续专项把归档版本与 HEAD 对齐（超出本轮"定点修复"边界，且需要对 V28 历史行为做出演进决策）。

## HOLD-5 ｜ Zironic/H3-Optimizations 上游无 LICENSE

- GitHub API 显示该仓库 **无 LICENSE 文件**（`license == null`）。本轮修正了台账（不再填写不实许可），并按"来源不明/许可未查实"登记。
- **未决**：是否继续引用该节点（引用安装不构成分发，风险较低），或寻找替代实现。不建议自行推断其许可。

---

**验收纪律声明**：以上 HOLD 均为登记性质；除 HOLD-4 的既有漂移外，其余不阻塞候选发布，但**发布说明中必须如实披露**，不得表述为"全部通过、无遗留"。
