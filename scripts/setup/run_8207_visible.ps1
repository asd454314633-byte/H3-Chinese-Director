# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
﻿$ErrorActionPreference='Stop'
$taskRoot='<REDACTED_LOCAL_PATH>/D'
$Host.UI.RawUI.WindowTitle='ComfyUI 8207 - 中文导演台隔离验证 - http://127.0.0.1:8207'
Set-Location -LiteralPath (Join-Path $taskRoot 'runtime')
$env:PYTHONUNBUFFERED='1'

Start-Transcript -Path (Join-Path $taskRoot 'logs\visible_console.log') -Append
Write-Host '中文导演台隔离环境：http://127.0.0.1:8207'
try {
 & '<REDACTED_LOCAL_PATH>/D' -u main.py --windows-standalone-build --disable-xformers --disable-comfy-compiler --listen 127.0.0.1 --port 8207 --input-directory "$taskRoot\runtime\input" --output-directory "$taskRoot\runtime\output" --temp-directory "$taskRoot\runtime\temp" --user-directory "$taskRoot\runtime\user" --database-url 'sqlite:///:memory:'
} finally { Stop-Transcript; Read-Host '服务已退出。按回车关闭窗口' }
