# MiniMax 官方 H3 提示词写作 Skill — 外部依赖（不随本仓库分发）

> **本目录原名 `official-minimax-h3-prompt`，曾包含三份 MiniMax 官方原版文件。
> 经 2026-10-13 归属审计复核，这三份文件已确认是上游原版内容，
> 已从本公开仓库中排除。** 本目录现在只保留「来源指针 + 取证证据 + 安装入口」，
> 不再包含任何上游正文。

## 1. 被排除的三份文件（原样引用，不再声称原创）

| 公开包内的旧路径 | 上游仓库 | 上游路径 | 上游 blob SHA1 | 上游字节 |
|---|---|---|---|---|
| `skills/official-minimax-h3-prompt/SKILL.md` | MiniMax-AI/MiniMax-H3 | `skills/h3-prompt-writing/SKILL.md` | `b6d9b2839384a588763a9c24315225dd8ce19d56` | 2623 |
| `skills/official-minimax-h3-prompt/references/base-en.txt` | MiniMax-AI/MiniMax-H3 | `skills/h3-prompt-writing/references/base-en.txt` | `40cf586a634d677d6b7107b367cf0ec9621be728` | 15773 |
| `skills/official-minimax-h3-prompt/references/ref-en.txt` | MiniMax-AI/MiniMax-H3 | `skills/h3-prompt-writing/references/ref-en.txt` | `7ae1b2d07d743fd2392258a96449be9e9e322d35` | 23553 |

同一内容在上游仓库内还有 `.agents/skills/h3-prompt-writing/` 与
`.claude/skills/h3-prompt-writing/` 两份同字节镜像（`base-en.txt` / `ref-en.txt`
blob 与 `skills/` 下完全一致；`SKILL.md` 在 `.agents`/`.claude` 下为 2177 B 的
`066429d78f72b080a52350a5b165e52cb31b0bca`，与 `skills/` 下的 2623 B 版本不同）。

## 2. 内容比对证据（判定为「官方原版」的依据）

审计把公开包内文件去掉本地 255–256 字节脱敏横幅后，与上游 HEAD 做换行归一化比对：

| 文件 | 去横幅后字节 | 归一化后 SHA256 | 上游归一化 SHA256 | 归一化逐字节相等 |
|---|---|---|---|---|
| `SKILL.md` | 2663 | `a7000443588ca3f145e3b3fd8900f14e0325dc460bd811268fac89a9dc8e56d0` | 同左 | **是** |
| `references/base-en.txt` | 15995 | `2cfebc096a6e08370f288d468d90b60f7f9bcb938f94bf090816e910e48e75fc` | 同左 | **是** |
| `references/ref-en.txt` | 23553† | `1e574f356716ad55612247ffb7bbccbcdb484ad96599d63c7dca1af186b1fab7` | 同左 | **是** |

† `ref-en.txt` 去横幅后仍为 CRLF 行尾；括号内为与上游 LF 版本比对前的字节数。
差异形态为**纯行尾（CRLF↔LF）+ 一行脱敏横幅**，不存在内容级改写。
另按行块覆盖度独立复核：`ref-en.txt` 对上游三处镜像的覆盖率均为 **99.57%（229/230 行）**，
唯一未覆盖行即脱敏横幅所在行。

⇒ 结论：这三份文件是 **MiniMax 官方原版逐字内容**，此前把它们统计进
「本项目自研原创 A 类」是错误的（见 `OWNERSHIP_CORRECTIONS.csv`）。

## 3. 许可状态：**LICENSE_HOLD（未取得再分发授权）**

- GitHub API `repos/MiniMax-AI/MiniMax-H3` 的 `license` 字段为 **`null`**
  （2026-10-12 与 2026-10-13 两次核实一致），仓库根目录无 `LICENSE` /
  `LICENSE.md` / `LICENSE.txt`（`LICENSE.md`、`LICENSE.txt` 均 HTTP 404）。
- Hugging Face 模型卡附带一份 **17,604 B 的 MiniMax H3 Community License Agreement**，
  其条款包含：再分发须逐字附带 NOTICE、禁止附加不同条款、以及
  **地域限制（排除部分司法辖区）**。本仓库 `git grep -iE "community license|MiniMax H3 is licensed"` 命中 0。
- 因此：**本仓库不持有一份可据以再分发这三份文件的明确授权**；
  同时也**不能**对它们施加本仓库的 MIT —— 此前 `LICENSE` 对全部 authored surface
  统一声明 MIT 的做法对这三份文件是**越权授权**，已修正。

**处置**：不自动下载、不捆绑、不重新分发。需要使用者自行从官方渠道取得，
并遵守其自身许可与地域限制。再分发授权仍列为 **HOLD**，等待书面确认或改为纯引用。

## 4. 本项目是否依赖它：是（运行时弱依赖）

`H3_V28_Director/v28_h3_format.py` 会从本目录读 `references/ref-en.txt`，
用于解析官方六段标题与 retention marker 枚举。因此本目录不是纯文档，
排除官方正文后必须走外部安装，否则相关校验无法运行。

依赖解析顺序（由 `v28_h3_format.resolve_guide_path()` 实现）：

1. 环境变量 `H3_MINIMAX_OFFICIAL_SKILL_DIR`
   —— 指向一个含 `references/ref-en.txt` 的目录；
2. 本目录（即你把官方文件安装回 `skills/official-minimax-h3-prompt/` 的情形）；
3. 都找不到 → **抛 `H3OfficialGuideMissing`**，错误信息里直接给出缺失文件、
   已尝试的路径、以及安装命令（不会退化成裸 `FileNotFoundError`，
   也不会静默关闭六段校验）。

## 5. 安装（本地，非分发）

推荐：从官方渠道取得副本后，用随包脚本按 blob SHA1 校验并安装。

```bash
python scripts/setup/install_minimax_official_skill.py --source <你本地的 MiniMax-H3 副本>
python scripts/setup/install_minimax_official_skill.py --verify          # 只校验已安装副本
```

脚本默认**不联网下载**。若确需下载，必须显式加
`--allow-download --i-have-license-rights`，脚本会先打印第 3 节的 HOLD 提示。

安装后校验：

```bash
python -c "from v28_h3_format import official_guide_status; print(official_guide_status())"
```

## 6. 与官方六段契约的关系（不因排除官方文件而改变）

官方六段标题为
`subject_definitions / summary / retention_analysis / detailed_description /
overall_soundscape / non_diegetic_music`。
本项目 `v28_director_core.py` 与 `v28_prompt_compiler.py` 各自**独立持有同一份
自研 `SECTIONS` 常量**（与官方解析结果逐项相同），因此六段导演与自研编译器
**不依赖官方文件即可正常工作**；官方文件只用于 `v28_h3_format` 的
marker 枚举与官方文案校验。
