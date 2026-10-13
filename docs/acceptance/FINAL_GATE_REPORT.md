# V29.4 发布前定点核查报告（FINAL GATE REPORT）

- 候选分支：`remediation/v29.4` @ `b0c59ec`（前序 `946f40d`；基线 `40e1a0f`；未推送、未合并 main、未发布 Release）
- 唯一工作流：Blob `aadee988ad2cce4d946e9054643a72f4d0e41d6b` **未改动任何字节**（验收 F1/F2 复核一致；181 节点/218 连线/2 子图）
- 冻结 8197 生产环境：本轮零接触
- 最终离线验收：**PASS=33 / FAIL=0 / HOLD=2**

---

## 一、五项残余风险逐项是否阻塞发布

| # | 风险 | 判定 | 依据 |
|---|---|---|---|
| 1 | MiniMax 官方 Skill 许可（永久排除方案） | **不阻塞** | 三份官方原版文件不在公开包（隔离安装复核 I-A 确认）；skills/official-minimax-h3-prompt/ 仅存 README（含官方安装链接、三个 blob SHA1、归属声明、LICENSE_HOLD 说明）；`v28_h3_format` 缺失时抛 `H3OfficialGuideMissing`（含安装命令），**无静默回退**（隔离故障注入 I-C 证明）；配置后六段契约正常解析（正控制 I-D，SECTIONS=6） |
| 2 | 工作流 11 处占位符 | **不阻塞** | 逐处定性见下节；核心执行路径无占位符依赖 |
| 3 | 语义占位符 | **不阻塞（已处置）** | 原 75 处 → 56 处；**19 处功能性占位符已全部修复或中性化**（见下节），"核心运行影响"类 = **0 处**；剩余 56 处均为测试夹具/docstring/工具说明 |
| 4 | V28 测试套件既有失败 | **不阻塞（FAIL/HOLD 如实登记）** | 与基线逐项对比 **F=16/E=56 完全一致（零新增）**；失败全部归因：测试夹具占位符在 Windows 非法（~15）、私有归档版本漂移（~55：KeyError reference_contract ×12、MANUAL_* 属性缺失 ×6、G2/G4 期望差异等）、测试基础设施（double module identity ×6）。未删除任何测试、未改任何断言标准。V29 生产链必需测试全绿：test_workflow_structure 13/13、test_public_release_scope 7/7、test_gate_repair 17/17 |
| 5 | Zironic/H3-Optimizations 许可 | **不阻塞（HOLD 保留）** | 分目录确认（raw 取证，native_LICENSE.txt SHA256 `cd1c9ea1…` 留档）：`native/LICENSE` 为 Apache-2.0 且版权方是 **Comfy Org**（vendored 自 ComfyUI 上游，不能代表整包）；仓库其余部分根目录**无 LICENSE**，按版权保留处理。THIRD_PARTY_NOTICES §3 与 UPSTREAM_ATTRIBUTION 已按目录口径修正。本仓库引用安装、不分发其源码；既不把 Apache-2.0 扩展到整包，也不武断判"整包无许可"。是否继续引用留待您裁决 |

## 二、两项验收 HOLD 的准确名称、影响与判断依据

**HOLD-1 ｜ D2 语义位置占位符（修复后余 56 处）**
- **影响**：0 处影响核心运行；1 处影响可选功能（H3_Prompt_Sidecar `director_engine.py:146` 规则文本损失，已由 `REDACTED_RULE_SLOTS` 显式登记）；其余 55 处仅影响说明文字/测试数据（测试夹具中的 `<REDACTED_MEDIA>`/`<REDACTED_LAN_IP>` 是合法的"任意字符串"测试值，语义等价于随机样本，不影响测试有效性）。
- **判断依据**：AST 全树扫描逐项人工定性；19 处功能性占位符（dialogue_mode 默认值 ×4、可诊断错误消息 ×2、mock 演示文本 ×3、ffprobe 失效兜底 ×1、gemma ROOT/MODEL ×2、prebake 缓存根 ×1、transfer audit 输出 ×1、规划/编译模板对白规则行 ×2、docstring ×1、UI 回退文本 ×1）已修复并经回归对比（零新增失败）。规划/编译模板的两条对白规则行按上下文重构为中性引导句（**非逐字恢复**，已注明）。

**HOLD-2 ｜ D3 冻结工作流占位符（11 处 = 4 个物理值）**
- **影响与定性**：
  - **8 处**（节点 #687–690 LoadImageCrop × `widgets_values[0]` + `widgets_values_named.image` 两个视图）：值为 `H3_NVFP4_AB_20261006/Qwen_image_2.<REDACTED_MEDIA>` → **正常待填写值**（参考图装载槽，用户必须装载自己的图；缺图时上游节点明确报"文件不存在"，非静默错误路径）。文件名残留占位符属脱敏产物，发布说明需提示用户装载参考图。
  - **3 处**（`extra.audio8_baseline` / `extra.h3_pass1_repair_evidence` / `extra.h3_source_v016`，值为 `<REDACTED_LOCAL_PATH>/C|D|E`）→ **脱敏造成的信息损失，不影响运行**：全仓代码零引用这三个键，ComfyUI 不执行 `extra` 块，属历史谱系元数据。
- **判断依据**：JSON 语义级解析 + 全根遍历定位；`grep` 证明三键无运行时读取者。**核心执行路径无无法解析的必需参数 → 不构成发布阻塞。**

## 三、全新隔离安装：通过（9/9 PASS）

在全新临时目录复制安装公开包（非引用生产模块），证据 `evidence/isolated_install_v29_4.json`：

| 项 | 结果 |
|---|---|
| I-A 复制安装 + 官方 Skill 原版文件不存在 | PASS |
| I-B 四个补齐 V28 模块可导入（包方式） | PASS |
| I-C 官方 Skill 缺失 → `H3OfficialGuideMissing`（无静默回退） | PASS |
| I-D 配置 Skill 后六段契约解析（SECTIONS=6，正控制） | PASS |
| I-E AudioRefine 缺失 → 明确报错含安装指引 | PASS |
| I-F AudioRefine 安装器（本地副本，标准 vendor 布局，不联网） | PASS |
| I-F2 安装后运行时解析链正控制（VENDOR/SHA 解析） | PASS |
| I-G 路径未配置 → 拒绝创建（故障注入） | PASS |
| I-H 配置后运行时目录可建立（正控制） | PASS |

**未实测声明**：音频精修执行、视频生成、Gemma 本地推理为 GPU 能力，本验收仅覆盖导入/配置/依赖解析/故障注入，**均标记为未实测**，不作为运行 PASS。

## 四、全部修订文件清单与测试结果

**本轮（发布前核查）修改 14 文件**（commit `b0c59ec`，+59/−76）：
`v28_director_core.py`（dialogue_mode 默认值、可诊断错误消息）、`v28_state_machine.py`（UI 回退、删除失效 ffprobe 兜底）、`v28_orchestrator.py`（默认值 ×2）、`v28_routes.py`（默认值）、`v28_mock_provider.py`（演示文本 ×3）、`v28_gemma_runtime.py`（ROOT/MODEL env 化）、`v28_director_prompts.py`（模板对白规则行中性重构 ×2）、`h3_conditioning_prebake/cache_codec.py`（ROOT env 化 + 明确报错）、`h3_transfer_audit/__init__.py`（DEST env 化 + 明确报错）、`THIRD_PARTY_NOTICES.md` 与 `docs/UPSTREAM_ATTRIBUTION.md`（Zironic 分目录口径）、`docs/acceptance/acceptance_v29_4.json/.log`、`candidate_file_manifest.csv`。

**累计候选差异**：基线 `40e1a0f` → `b0c59ec`，24+9=33 个修改文件、13 新增、3 删除（逐文件要点见 RELEASE_CANDIDATE_DIFF.md）。
**私人信息复查**：14 个修订/新增文件深度扫描（用户名/私人盘符/归档目录/密钥形态/真实 IP）——唯一命中为验收记录内本机临时目录路径，已脱敏并修改验收器写盘逻辑（现自动 `%TEMP%` 化），终态 **0 残留**（证据 `evidence/private_info_scan.json` + `acceptance_v29_4_final.json`）。

**测试结果汇总**：
- 离线验收 33 PASS / 0 FAIL / 2 HOLD（含 I2 正控制：注入真过宽声明 → FAIL 捕获 → 还原 → PASS，检查器有效性自证）
- V29 生产链必需测试：13/13 + 7/7 + 17/17 全 PASS
- V28 全量套件：ran=285，F=16/E=56/skipped=14 —— 与基线完全一致（零新增），失败全为历史版本测试/夹具损失，FAIL/HOLD 如实保留
- 隔离安装验收：9/9 PASS

## 五、RELEASE_READY = **YES**（候选层面）

- 七项发布前核查全部完成，无新增阻塞项；唯一工作流字节未动；生产零接触；未推送/未合并/未发布。
- **附带条件（由您在批准发布时确认）**：
  1. 发布说明必须包含：MiniMax Skill 永久排除与安装指引、参考图槽需用户装载、Zironic 许可分目录口径、无 GPU 实测范围声明；
  2. V28 历史测试的既有失败（版本漂移 + 夹具损失）是否列入后续修复计划由您裁决，不影响本版发布；
  3. 正式发布动作（merge/tag/Release）由您执行，本轮未做。
