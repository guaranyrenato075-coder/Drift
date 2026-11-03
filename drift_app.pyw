"""
CutWire Drift AI - Unified Desktop Application Launcher
Seamlessly unites the AI Factory, Batch Producer, and Drift Video Editor
into a single, native, zero-console desktop window.
"""
import sys
import os
import time
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
AI_SERVER_SCRIPT = BASE_DIR / "drift-ai-editor" / "web_ui.py"
DRIFT_EXE = BASE_DIR / "Drift" / "drift.exe"
HEALTH_URL = "http://127.0.0.1:8765/api/health"

EDGE_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

def find_edge() -> Optional[Path]:
    for p in EDGE_PATHS:
        if p.exists():
            return p
    return None

def is_ai_running() -> bool:
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "Drift-App/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_ai_server() -> Optional[subprocess.Popen]:
    if is_ai_running():
        return None

    python_dir = Path(sys.executable).parent
    pythonw = python_dir / "pythonw.exe"
    exe_to_use = str(pythonw) if pythonw.exists() else sys.executable

    no_window = 0x08000000 if os.name == "nt" else 0
    proc = subprocess.Popen(
        [exe_to_use, str(AI_SERVER_SCRIPT)],
        cwd=str(AI_SERVER_SCRIPT.parent),
        creationflags=no_window,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Aguarda o servidor responder na porta 8765
    for _ in range(30):
        if is_ai_running():
            break
        time.sleep(0.2)

    return proc

def main():
    # 1. Inicia o motor de IA em segundo plano
    ai_proc = start_ai_server()

    # 2. Localiza o executável Edge App Mode
    edge_exe = find_edge()
    profile_dir = BASE_DIR / ".app_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    app_args = [
        str(edge_exe),
        "--app=http://127.0.0.1:8765",
        f"--user-data-dir={str(profile_dir)}",
        "--window-size=1380,880",
        "--disable-extensions",
        "--disable-default-apps",
        "--no-first-run"
    ] if edge_exe else ["python", "-m", "webbrowser", "http://127.0.0.1:8765"]

    no_window = 0x08000000 if os.name == "nt" else 0
    try:
        # Abre o aplicativo como uma janela nativa de desktop independente
        app_proc = subprocess.Popen(app_args, creationflags=no_window)
        app_proc.wait()
    finally:
        # Encerramento gracioso ao fechar o app
        if ai_proc and ai_proc.poll() is None:
            ai_proc.terminate()

if __name__ == "__main__":
    main()
