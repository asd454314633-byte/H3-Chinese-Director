# Windows 环境安装 / 启动 / 验证 / 排错 / 升级与回滚（8197 正式公开版）

> 文件名中的 `8207` 为旧版兼容名称，本指南实际只针对公开的 **8197 生产线**。端口可以自行选择，不能由文档文件名推断运行路线。

本公开包**只发布 8197 冻结生产线**：唯一工作流
`workflows/current/V29_chinese_director_production_8197.json` 与
`custom_nodes/local_author/8197_production_line/` 自研源码。
8207 实验线源码**不在本公开包内**（仅保留在作者本机生产归档）；下表说明两条线的验收边界，
避免把 8197 的验收结论误用到未公开、未同等验收的 8207 线。

---

## 0. 两条线的验收边界（8197 公开 / 8207 不公开）

| 维度 | 8197（冻结生产，公开包内） | 8207（独立运行/实验，**不在公开包内**） |
|---|---|---|
| 定位 | 已冻结的生产线，变更受治理 | 独立环境，用于并行开发与实验 |
| 前端 | 含 GUIDE 权威归一补丁 | 冻结件不含该补丁，已停止使用 |
| 节点 | 8197 线快照（含 `H3_Audio8Step`、`H3_AudioUpgrade`、`H3_NextgenDirector`、`H3_V29_ManualChainMerge` 等） | 8207 线快照（含 `H3_Qwen21_NoteShim`、`comfyui-krea2edit`、`krea-reference`） |
| 验收 | 六段真实生成 + 自动合并 PASS | **GPU 生成未做同等验收** |

**结论**：任何"8197 跑过所以 8207 没问题"的推断都不成立。8207 的功能项在 `docs/FEATURE_MATRIX.md` 中单独标注，大多为 `NOT_TESTED` / `PARTIAL`；安装本公开包**不需要** 8207 线源码，也不需要其专用的第三方节点（`krea-reference` / `comfyui-krea2edit`）。

---

## 1. 前置条件

- Windows 10/11 x64
- NVIDIA GPU（H3 32B 级 TE + 主模型，建议 ≥ 24 GB 显存；本仓库实测采样峰值 22016 MiB）
- 系统内存：建议 ≥ 64 GB（实测可用 RAM 最低降到 5.94 GiB，Commit 采样峰值 95.05 GiB）
- Python 3.11+（与你的 ComfyUI 版本匹配）、匹配版本的 PyTorch + CUDA
- `ffmpeg` 可执行文件在系统 PATH（合并与音频链路需要）
- 磁盘：模型权重体积巨大（数十 GB 量级），请预留

## 1.1 Git 客户端预配置（Windows 必做一次）

Windows 对长路径有限制；建议 Git 启用长路径支持。**本仓库现已提供 `.gitattributes`，将源码和 JSON 的换行规则固定为 LF**，不再要求修改整台电脑的全局 `core.autocrlf`。验证字节一致性时仍应以 Git Blob 为准。

```bat
:: ① 允许 Git 处理长路径（只影响 Git，不动系统注册表）
git config --global core.longpaths true

:: ② 验证长路径配置；仓库级 .gitattributes 管理 LF，无需更改全局 autocrlf
git config --global core.longpaths
```

克隆本仓库并核对完整性（可选但推荐）：

```bat
set "REPO=%USERPROFILE%\H3-Chinese-Director"
git clone https://github.com/asd454314633-byte/H3-Chinese-Director.git "%REPO%"
cd /d "%REPO%"
git ls-files workflows | find /c /v ""            :: 必须输出 1（唯一公开工作流）
git ls-files | findstr /B "history/ workflows/history/ manifests/public_files.csv"
                                                   :: 必须无任何输出（历史档案已退出公开包）
```

> 系统级长路径开关（`HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled=1`，需管理员并重启）可让 Python 等程序直接访问长路径，非必需；不开启时，用 Python 脚本访问本仓库深层文件请使用 `\\?\` 路径前缀。

## 2. 一步步安装

以下所有 `cd` 均从统一工作根目录 `%BASE%` 出发，避免相对路径错位；每段开头都显式回到 `%BASE%`。

```bat
set "BASE=%USERPROFILE%\comfy"
mkdir "%BASE%" 2>nul
```

### 2.1 ComfyUI

```bat
cd /d "%BASE%"
git clone https://github.com/Comfy-Org/ComfyUI.git
cd /d "%BASE%\ComfyUI"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2.2 第三方自定义节点

> **版本锁定**：下表为本仓库实际验证过的第三方节点提交（来源 `manifests/nodes.csv` 的本地 HEAD 记录）。锁定提交可复现验证环境；不锁定则拉到上游最新版，行为可能漂移。

| 目录名 | 上游仓库 | 已验证提交 |
|---|---|---|
| ComfyUI-KJNodes | kijai/ComfyUI-KJNodes | `d3cfe21625e5` |
| rgthree-comfy | rgthree/rgthree-comfy | `13b4399c00b5` |
| ComfyUI-MAINodes | matlowai/ComfyUI-MAINodes | `b99bb83f1b02` |
| ComfyUI-Ref2VA-VSA | Kablex/ComfyUI-Ref2VA-VSA | `92e3f8357c62` |
| ComfyUI-MiniMax-H3-PDD-Acc | Jalen-Brunson/ComfyUI-MiniMax-H3-PDD-Acc | `993566bd49a4` |
| ComfyUI-H3-Motion-Context | NikoDemon80/ComfyUI-H3-Motion-Context | `5335715abe54` |
| H3-Optimizations | Zironic/H3-Optimizations | `862774944a33` |
| comfyui-obvpm | obvpm/comfyui-obvpm | `7d5b977add00` |

```bat
cd /d "%BASE%\ComfyUI\custom_nodes"

git clone https://github.com/kijai/ComfyUI-KJNodes.git && git -C ComfyUI-KJNodes checkout d3cfe21625e5
git clone https://github.com/rgthree/rgthree-comfy.git && git -C rgthree-comfy checkout 13b4399c00b5
git clone https://github.com/matlowai/ComfyUI-MAINodes.git && git -C ComfyUI-MAINodes checkout b99bb83f1b02
git clone https://github.com/Kablex/ComfyUI-Ref2VA-VSA.git && git -C ComfyUI-Ref2VA-VSA checkout 92e3f8357c62
git clone https://github.com/Jalen-Brunson/ComfyUI-MiniMax-H3-PDD-Acc.git && git -C ComfyUI-MiniMax-H3-PDD-Acc checkout 993566bd49a4
git clone https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context.git && git -C ComfyUI-H3-Motion-Context checkout 5335715abe54
git clone https://github.com/Zironic/H3-Optimizations.git && git -C H3-Optimizations checkout 862774944a33
git clone https://github.com/obvpm/comfyui-obvpm.git && git -C comfyui-obvpm checkout 7d5b977add00
```

> 上表即本公开包所需的**全部**第三方自定义节点。`krea-reference` / `comfyui-krea2edit` 为 8207 实验线专用，**不在本公开包内、也无需安装**（归属登记见 `manifests/nodes.csv` 与 `docs/UPSTREAM_ATTRIBUTION.md`）。

> **前端版本门禁**：保持在 `COMFYUI_FRONTEND_VERSION_LOCK = 1.52.7`。1.53.6 存在「tab 切换恢复 `mode=0`」的已知回归，升级前必须加回归测试。

### 2.3 本地作者自研节点

把本仓库内容复制到 ComfyUI（公开包内只有 **8197 冻结生产线**）。以下命令使用前面克隆时设置的 `%REPO%`，不要把 `<repo>` 之类的尖括号占位符直接粘贴到 Windows CMD（会被解析为重定向）：

```bat
xcopy /E /I /Y "%REPO%\custom_nodes\local_author\8197_production_line\*" "%BASE%\ComfyUI\custom_nodes\"
```

> 8207 实验线源码不在本公开包内，无需也无法安装；本仓库不提供第二条线的复制命令。

### 2.4 外部依赖（需要相关功能时安装）

官方 MiniMax Skill 和音频精修源码不随仓库重新分发。**请先自行确认上游许可并获得对应源码副本**；下面仅是路径示例，`%USERPROFILE%\MiniMax-H3` 和 `%USERPROFILE%\ComfyUI-H3-AudioRefine` 必须是你实际取得的上游目录。

```bat
python "%REPO%\scripts\setup\install_minimax_official_skill.py" --source "%USERPROFILE%\MiniMax-H3" --dest "%BASE%\ComfyUI\custom_nodes\H3_V28_Director\skills\official-minimax-h3-prompt"
python "%REPO%\scripts\setup\install_h3_audio_refine.py" --source "%USERPROFILE%\ComfyUI-H3-AudioRefine" --dest "%BASE%\ComfyUI\custom_nodes\H3_AudioUpgrade\vendor"
python "%REPO%\scripts\setup\install_minimax_official_skill.py" --verify --dest "%BASE%\ComfyUI\custom_nodes\H3_V28_Director\skills\official-minimax-h3-prompt"
python "%REPO%\scripts\setup\install_h3_audio_refine.py" --verify --dest "%BASE%\ComfyUI\custom_nodes\H3_AudioUpgrade\vendor"
```

安装器默认写入公开仓库副本内的路径；若用户已经复制节点到 ComfyUI，务必像上例一样显式指定 `--dest`。AudioRefine 安装器**没有** `--allow-download` 参数；官方 Skill 安装器有联网选项，但默认不联网，且须自行确认许可。

### 2.5 模型

按 [`docs/MODELS.md`](MODELS.md) 自行下载，放到对应目录。可用 `config/examples/extra_model_paths.example.yaml` 作为 `extra_model_paths.yaml` 的模板（**把 `base_path` 改成你自己的路径**）。

### 2.6 工作流

把 `workflows/current/V29_chinese_director_production_8197.json` 放入 `ComfyUI/user/default/workflows/`，或在前端直接导入。

## 3. 启动

```bat
cd /d "%BASE%\ComfyUI"
.venv\Scripts\activate
python main.py --port 8197
```

端口 `8197` 只是示例，已占用时改用其他空闲端口；不能通过改端口把 8197 工作流变成 8207 实验线。

以下为历史 8207 辅助脚本（**不是本公开包的必需启动流程**，不建议新用户执行）：

- `scripts/setup/launch_8207_visible_host.py` —— 可见控制台启动（Windows 交互式会话）
- `scripts/setup/run_8207_visible.ps1` —— PowerShell 启动包装
- `scripts/setup/8207_prepare.py` / `8207_finalize.py` / `8207_complete_mirror.py` —— 并行环境准备与收口
- `scripts/verify/8207_acceptance_report.py` —— 验收报告生成

> Windows 上启动需要**交互式桌面会话**（不能用 Session 0 / SYSTEM）。若"双击没反应"，多为进程秒退或被系统当作挂起关闭，请改用可见控制台方式启动看日志。

## 4. 验证

### 4.1 无需模型的验证（推荐先做）

在**本仓库根目录**执行（`<repo>` 为你克隆本仓库的路径）：

```bat
cd /d "%REPO%"
python scripts/verify/verify_workflow_structure.py
```

会检查：JSON 可解析、节点/连线完整性、必需节点存在、六段状态为中性默认、无私有路径/素材残留。

### 4.2 加载验证

1. 启动 ComfyUI，导入工作流
2. 检查是否有**红色缺失节点** → 有则说明对应自定义节点未安装
3. 检查 `UNETLoader` / `CLIPLoader` / `VAELoader` / `LoraLoaderModelOnly` 的下拉是否有值 → 空则权重未放到位
4. 只操作画布上「H3 全中文傻瓜导演台」唯一入口

### 4.3 GPU 生成验证（需自行执行）

> 本仓库**不会**自动发起 GPU 压力测试。请自行确认显存/内存余量后再跑。
> 若内存紧张（`MEMORY_MARGIN = LIMITED`），不要叠加额外常驻优化而不做验收。

## 5. 排错

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 前端出现红色缺失节点 | 自定义节点未安装或版本不匹配 | 按 `docs/UPSTREAM_ATTRIBUTION.md` 补齐并重启 |
| 模型下拉为空 | 权重目录不对 | 对照 `docs/MODELS.md` 与 `extra_model_paths.yaml` 的 `base_path` |
| 六段按钮点了没反应 | `continuous=false` 默认值 + guard | 本仓库已修复该 NOOP（执行态初始化 + 显式批量自动开启），请确认加载的是本仓库版本的前端 |
| GUIDE 开关被自动翻回 | 使用了不含 GUIDE 权威补丁的 8207 冻结前端 | 改用 8197 线前端 |
| tab 切走再切回，开关变回默认 | ComfyUI 前端 1.53.6 回归 | 锁定 1.52.7 |
| 启动无窗口/秒退 | 非交互式会话启动 | 用 `scripts/setup/launch_8207_visible_host.py` 或可见控制台 |
| 合并失败 | `ffmpeg` 不在 PATH | 安装并把 `ffmpeg` 加入 PATH |
| 显存/Commit 打满 | 内存余量有限 | 参考 `docs/ARCHITECTURE.md` 第 4 节生命周期，不要盲目叠加优化 |

## 6. 升级

1. 先备份 `custom_nodes/` 与 `user/default/workflows/`
2. 升级**第三方节点**时逐个升级并单独验证（不要一次全升）
3. 升级 **ComfyUI 前端**前必须验证 tab 切换双态保持
4. 升级后重跑 `scripts/verify/verify_workflow_structure.py`

## 7. 回滚

1. 恢复 `custom_nodes/` 备份
2. 恢复工作流：本仓库只发布唯一 V29 冻结生产工作流；**历代工作流不在公开包内**，如需版本回退请
   用 `git log -- workflows/current/V29_chinese_director_production_8197.json` 回溯本仓库自身的提交历史，
   或向作者申请对应时点的生产归档（历史档案仅在本机生产侧保留）
3. 恢复前端版本锁：`COMFYUI_FRONTEND_VERSION_LOCK = 1.52.7`
4. 前端回滚后再验证六段状态可加载
