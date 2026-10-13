# RELEASE_CANDIDATE_DIFF — V29.4 候选逐文件差异

基线：`40e1a0f0dfa62f3f32923a41d1c4c579dd0dca8e`（origin/main）→ 候选：`remediation/v29.4`
合计：24 文件修改（+931 / −138 行），13 文件新增，3 文件删除。

## 一、修改的文件（git diff --stat 原样）

```
AUTHOR_CONTRIBUTIONS.md                            | 143 +++++++++++++++---
LICENSE                                            |  85 ++++++++---
README.md                                          |  28 +++-
README_EN.md                                       |  44 +++++-
THIRD_PARTY_NOTICES.md                             | 165 +++++++++++++++++----
custom_nodes/.../H3_AudioUpgrade/nodes.py          |  16 +-
custom_nodes/.../H3_MemoryPolicy.disabled/__init__.py | 126 ++++++++++++++--
custom_nodes/.../H3_Prompt_Sidecar/START_H3_DIRECTOR.ps1 |   4 +-
custom_nodes/.../H3_Prompt_Sidecar/director_engine.py |   5 +-
custom_nodes/.../H3_Prompt_Sidecar/director_rules.py |  29 +++-
custom_nodes/.../H3_V28_Director/tests/_v28_bootstrap.py |  87 ++++++++++-
custom_nodes/.../H3_V28_Director/tests/test_v28_isolation.py |  21 ++-
custom_nodes/.../H3_V28_Director/tests/test_v28_state_machine.py |  14 +-
custom_nodes/.../H3_V28_Director/v28_paths.py      | 111 +++++++++++++-
custom_nodes/.../h3_conditioning_audit_probe_20261004.disabled/__init__.py | 22 ++-
custom_nodes/.../h3_workflow_helpers/web/h3_foolproof_v3_dashboard.js |   6 +-
docs/UPSTREAM_ATTRIBUTION.md                       |  54 ++++++-
manifests/nodes.csv                                |  13 +-
scripts/setup/8207_complete_mirror.py              |   5 +-
scripts/setup/8207_finalize.py                     |   5 +-
scripts/setup/8207_prepare.py                      |  12 +-
scripts/setup/launch_8207_visible_host.py          |   5 +-
scripts/setup/run_8207_visible.ps1                 |  13 +-
scripts/verify/verify_source_usability.py          |  56 ++++++-
```

## 二、逐文件差异要点

| 文件 | 差异性质 | 风险评估 |
|---|---|---|
| `LICENSE` | 加 MIT 覆盖范围声明：不对 MiniMax 官方 Skill 原版（LICENSE_HOLD）与第三方原版授 MIT；SDPose 子图为 MIT 派生并附上游坐标；模型/ComfyUI 引擎/第三方节点均不随包 | 纯文档 |
| `README.md` / `README_EN.md` | 加"第三方内容与外部依赖"必读段；清除"完全原创/不含第三方"过宽断言（改为否定式更正声明）；安装步骤补两台安装器 | 纯文档 |
| `THIRD_PARTY_NOTICES.md` | 重写 §0–§7：总览表、ComfyUI GPL 许可边界、MiniMax HOLD、AudioRefine MIT 钉 fd5a8dfe、SDPose 蓝图派生（全等 + 80/10 修改清单）、来源不明、修改声明、未决 HOLD | 纯文档 |
| `AUTHOR_CONTRIBUTIONS.md` | 分类定义显式映射（A/B/C/D/E，含旧 E 含义冲突说明）；122/27/8 统计口径落地；§8 显存工程 B 类标注；音频链路降为 B 类包装层；"非原创部分"清单补全 12 项第三方 + SDPose 蓝图 + MiniMax Skill + PreviewImage | 纯文档 |
| `docs/UPSTREAM_ATTRIBUTION.md` | 补 Adudeguyman、MiniMax Skill、SDPose blueprint（commit `cdccb2ee`）、Zironic 无 LICENSE 修正、obvpm 改名说明；修复表格被引用块打断的排版 | 纯文档 |
| `manifests/nodes.csv` | 行 22/34/35 三处"vendor/LICENSE 随包"矛盾修正为外部依赖；H3_V28_Director 描述同步 skills/HOLD；SDPose 行补上游坐标；分类计数不变（A20/D15/C5/B1/E1），42×15 列校验通过 | 纯台账 |
| `H3_AudioUpgrade/nodes.py` | `from .vendor.nodes import …` → `audio_refine_loader.load_sampler_class()`；错误串占位符改可诊断中文 | 代码，静态验证 |
| `H3_MemoryPolicy.disabled/__init__.py` | G-1 重写：env `H3_MEMORY_POLICY_COMFY_ROOT` + `self_check()` 五态 | 代码，test_gate_repair 覆盖 |
| `H3_V28_Director/v28_paths.py` | G-3：三路径 env 化 + 哨兵 + `require_configured()` 前置 | 代码，test_gate_repair 覆盖 |
| `tests/_v28_bootstrap.py` | G-2：`watched_paths()`/`fingerprint_all()`/`detect_pollution()` + MODULES 追加 4 模块 | 代码，含正控制 |
| `test_v28_isolation.py` / `test_v28_state_machine.py` | 反污染测试未配置时 skipTest("HOLD — …")，不再恒真恒假 | 代码 |
| `h3_conditioning_audit_probe…/__init__.py` | 第 4 处占位路径 → env `H3_CONDITION_AUDIT_OUT` | 代码 |
| `director_rules.py` / `director_engine.py` | 移除 5 处语义位置占位符（规则文本置空 + `REDACTED_RULE_SLOTS` 登记损失） | 代码，语义损失已登记 |
| `h3_foolproof_v3_dashboard.js` | 修复被脱敏破坏的正则字符类（`h3DrExtractSection`） | 代码，JS 语法 PASS |
| `8207_prepare/finalize/complete_mirror/launch_host/run_visible.ps1` | 占位路径 → `h3_8207_paths.py` env 驱动；ps1 修 UTF-8 BOM 错位 | 代码，B4/G4 PASS |
| `verify_source_usability.py` | 新增 SEMANTIC 语义占位符检查（不并入 FAIL，输出 HOLD）；修 skipped 统计 | 验收工具 |

## 三、新增的文件（13 个）

| 文件 | 用途 |
|---|---|
| `H3_V28_Director/v28_h3_format.py` | 补齐缺失模块（懒加载官方 guide + 缺失明确报错） |
| `H3_V28_Director/v28_manual_continuation.py` | 补齐缺失模块（私有归档脱敏版） |
| `H3_V28_Director/v28_reference_contract.py` | 补齐缺失模块（同上） |
| `H3_V28_Director/v28_reference_hygiene.py` | 补齐缺失模块（同上） |
| `H3_AudioUpgrade/audio_refine_loader.py` | AudioRefine 外部依赖解析器 |
| `skills/official-minimax-h3-prompt/README.md` | 上游坐标 + HOLD + 依赖解析说明（原三份官方文件已删除，目录仅留此 README） |
| `scripts/setup/h3_8207_paths.py` | 8207 线统一路径配置（env 驱动） |
| `scripts/setup/install_h3_audio_refine.py` | AudioRefine 外部安装器（--source/--verify/--dest） |
| `scripts/setup/install_minimax_official_skill.py` | MiniMax Skill 安装器（默认不下载，双确认） |
| `scripts/verify/verify_sdpose_blueprint.py` | SDPose 蓝图复核（blob/SHA256/结构全等校验） |
| `tests/test_gate_repair.py` | 门禁修复验收 17 项（含正控制与故意失败路径） |
| `docs/evidence/README.md` + `docs/evidence/sdpose_blueprint_pinned.json` | 证据归档说明 + 钉住副本 |
| `docs/acceptance/*`（验收产物，不入发布包） | acceptance_v29_4.json/.log、candidate_file_manifest.csv |

## 四、删除的文件（3 个）

```
custom_nodes/.../H3_V28_Director/skills/official-minimax-h3-prompt/SKILL.md            (SHA256 d8708b5a…)
custom_nodes/.../H3_V28_Director/skills/official-minimax-h3-prompt/references/base-en.txt (SHA256 e703ad8f…)
custom_nodes/.../H3_V28_Director/skills/official-minimax-h3-prompt/references/ref-en.txt  (SHA256 24761e7b…)
```
删除依据：经 blob SHA1 比对确认为 `MiniMax-AI/MiniMax-H3` 官方原版（上游 `skills/h3-prompt-writing/`），非本作者创作；许可未查实，LICENSE_HOLD，不随包重分发。移除前 SHA256 已留档于本报告与 evidence。

## 五、未改动声明

- `workflows/current/V29_chinese_director_production_8197.json`：Blob `aadee988ad2cce4d946e9054643a72f4d0e41d6b`、SHA256（LF 归一化 `311609b1…`）均与基线一致；181 节点 / 218 连线 / 2 子图不变。
- 冻结 8197 生产环境（`D:\ComfyUI\ComfyUI_H3_V27_Lab`）：只读核查，零修改、零重启。
- 本机私有源码 / 历史归档 / 模型：零删除、零改动（仅只读定位与复制）。
