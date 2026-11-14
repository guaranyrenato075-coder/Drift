import sys
import os
import time
import subprocess
import urllib.request
from pathlib import Path

# Garante compatibilidade do Qt 6 com GPUs legadas (GeForce G210, etc.)
if "QSG_RHI_BACKEND" not in os.environ:
    os.environ["QSG_RHI_BACKEND"] = "opengl"

BASE_DIR = Path(__file__).resolve().parent.parent
AI_SERVER_SCRIPT = BASE_DIR / "drift-ai-editor" / "web_ui.py"
DRIFT_EXE = BASE_DIR / "Drift" / "drift.exe"
HEALTH_URL = "http://127.0.0.1:8765/api/health"

def is_ai_engine_running() -> bool:
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "Drift-Sidecar/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_ai_engine_daemon() -> subprocess.Popen:
    if is_ai_engine_running():
        return None

    no_window_flag = 0x08000000 if os.name == "nt" else 0
    proc = subprocess.Popen(
        [sys.executable, str(AI_SERVER_SCRIPT)],
        cwd=str(AI_SERVER_SCRIPT.parent),
        creationflags=no_window_flag,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(25):
        if is_ai_engine_running():
            break
        time.sleep(0.2)
    return proc

def main():
    ai_process = start_ai_engine_daemon()

    user_args = [a for a in sys.argv[1:] if a != "--agent-access"]
    if not user_args:
        default_proj = BASE_DIR / "Foco_Inabalável.drift"
        if default_proj.exists():
            user_args = [str(default_proj)]
    drift_args = [str(DRIFT_EXE), "--agent-access"] + user_args
    if not DRIFT_EXE.exists():
        print(f"Executável do Drift não encontrado em: {DRIFT_EXE}")
        if ai_process:
            ai_process.terminate()
        return

    # Garante que o processo herdará o backend OpenGL compatível
    env = os.environ.copy()
    env["QSG_RHI_BACKEND"] = "opengl"

    try:
        drift_proc = subprocess.Popen(drift_args, cwd=str(DRIFT_EXE.parent), env=env)
        drift_proc.wait()
    finally:
        if ai_process and ai_process.poll() is None:
            ai_process.terminate()

if __name__ == "__main__":
    main()
