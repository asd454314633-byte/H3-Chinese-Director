# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
# launch_8207_visible_host.py
# Persistent host for the OFFICIAL visible entry run_visible.ps1 (port 8207).
# Pattern proven by registry entries ComfyUI-DreamIDV-8194 / ComfyUI-H3-Live-8193:
# sandbox Job reclaims detached consoles -> must keep a host alive with p.wait().
# The ComfyUI console itself is VISIBLE (CREATE_NEW_CONSOLE) - never headless.
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from h3_8207_paths import task_root as _h3_task_root, python_exe as _h3_python_exe
TASK_ROOT = str(_h3_task_root())
ENTRY = os.path.join(TASK_ROOT, "run_visible.ps1")
PORT = 8207


def probe():
    """Payload-shape check, proxy BYPASSED (system proxy poisons localhost)."""
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with op.open("http://127.0.0.1:%d/system_stats" % PORT, timeout=3) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        return isinstance(d, dict) and "system" in d
    except Exception:
        return False


if probe():
    print("ALREADY_LISTENING", flush=True)
    sys.exit(0)

p = subprocess.Popen(
    ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
     "-File", ENTRY],
    creationflags=subprocess.CREATE_NEW_CONSOLE,  # VISIBLE black box
    cwd=TASK_ROOT,
)
print("HOST_CHILD_PID", p.pid, flush=True)

deadline = time.time() + 240
ok = False
while time.time() < deadline:
    if probe():
        ok = True
        break
    time.sleep(3)

print("READY" if ok else "READY_TIMEOUT", flush=True)
try:
    rc = p.wait()
    print("HOST_EXIT", rc, flush=True)
except KeyboardInterrupt:
    pass
