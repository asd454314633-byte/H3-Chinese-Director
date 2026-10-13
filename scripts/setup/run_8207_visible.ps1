# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
$ErrorActionPreference='Stop'
$taskRoot=$env:H3_8207_TASK_ROOT
$pythonExe=$env:H3_8207_PYTHON
if (-not $taskRoot) { throw "8207 隔离线路径未配置：请设置环境变量 H3_8207_TASK_ROOT 指向你的 8207 隔离环境根目录（其下有 runtime\ 与 logs\）。这是脱敏后的公开副本，私有原件里的真实本机路径不会被恢复、也不会被猜测。" }
if (-not $pythonExe) { throw "8207 隔离线的 Python 解释器未配置：请设置环境变量 H3_8207_PYTHON 指向 python.exe。" }
if (-not (Test-Path -LiteralPath $taskRoot)) { throw "H3_8207_TASK_ROOT 指向的目录不存在：$taskRoot" }
if (-not (Test-Path -LiteralPath $pythonExe)) { throw "H3_8207_PYTHON 指向的解释器不存在：$pythonExe" }
$Host.UI.RawUI.WindowTitle='ComfyUI 8207 - 中文导演台隔离验证 - http://127.0.0.1:8207'
Set-Location -LiteralPath (Join-Path $taskRoot 'runtime')
$env:PYTHONUNBUFFERED='1'

Start-Transcript -Path (Join-Path $taskRoot 'logs\visible_console.log') -Append
Write-Host '中文导演台隔离环境：http://127.0.0.1:8207'
try {
 & $pythonExe -u main.py --windows-standalone-build --disable-xformers --disable-comfy-compiler --listen 127.0.0.1 --port 8207 --input-directory "$taskRoot\runtime\input" --output-directory "$taskRoot\runtime\output" --temp-directory "$taskRoot\runtime\temp" --user-directory "$taskRoot\runtime\user" --database-url 'sqlite:///:memory:'
} finally { Stop-Transcript; Read-Host '服务已退出。按回车关闭窗口' }
