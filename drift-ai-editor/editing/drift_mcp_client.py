import subprocess
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

class DriftMcpClient:
    """
    Client for Drift's native Model Context Protocol (MCP) server over stdio.
    Launches and communicates with Drift in headless mode.
    """

    def __init__(self, drift_exe_path: Optional[str] = None):
        if drift_exe_path:
            self.drift_exe = Path(drift_exe_path)
        else:
            # Look in standard workspace locations
            base = Path(__file__).resolve().parent.parent.parent
            self.drift_exe = base / "Drift" / "drift.exe"

        self.process: Optional[subprocess.Popen] = None
        self._req_id = 1
        self.http_mode = False
        self.http_url = ""
        self.http_token = ""

    def _find_running_gui_session(self) -> Optional[Dict[str, Any]]:
        """Scans for an active Drift GUI editor instance with MCP enabled."""
        import glob
        import urllib.request
        temp_candidates = [
            os.environ.get("TEMP", ""),
            os.environ.get("TMP", ""),
            str(Path.home() / "AppData" / "Local" / "Temp")
        ]
        seen = set()
        for base in temp_candidates:
            if not base or not os.path.isdir(base):
                continue
            pattern = os.path.join(base, "drift", "mcp-sessions", "*.json")
            for sf in glob.glob(pattern):
                if sf in seen:
                    continue
                seen.add(sf)
                try:
                    with open(sf, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    port = data.get("port")
                    token = data.get("token")
                    if port and token:
                        health_url = f"http://127.0.0.1:{port}/health"
                        req = urllib.request.Request(health_url)
                        with urllib.request.urlopen(req, timeout=1.0) as resp:
                            if resp.status == 200:
                                return data
                except Exception:
                    pass
        return None

    def start(self):
        """
        Connects to Drift's MCP server.
        Prioritizes connecting directly to the running graphical editor window
        so that clip insertions appear live on screen in the active timeline!
        Falls back to starting a headless instance if no GUI is running.
        """
        # 1. Try to attach to the active graphical window
        gui_session = self._find_running_gui_session()
        if gui_session:
            self.http_mode = True
            port = gui_session["port"]
            self.http_token = gui_session.get("token", "")
            self.http_url = f"http://127.0.0.1:{port}/mcp"
            return {"active_gui": True, "port": port}

        # 2. Fall back to headless subprocess
        if self.process and self.process.poll() is None:
            return

        if not self.drift_exe.exists():
            raise FileNotFoundError(f"Drift executable not found at {self.drift_exe}")

        self.http_mode = False
        self.process = subprocess.Popen(
            [str(self.drift_exe), "--headless", "--isolated-session", "--mcp-stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # MCP handshake: initialize
        init_res = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "drift-ai-editor", "version": "1.0.0"}
        })

        # Send notifications/initialized
        self._send_notification("notifications/initialized", {})
        return init_res

    def stop(self):
        """Terminates headless Drift process (leaves running GUI intact)."""
        if self.http_mode:
            self.http_mode = False
            return
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                self.process.kill()
            finally:
                self.process = None

    def _next_id(self) -> int:
        req_id = self._req_id
        self._req_id += 1
        return req_id

    def _send_notification(self, method: str, params: Dict[str, Any]):
        if self.http_mode:
            # Notifications over HTTP are optional or sent as normal requests
            return
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Drift MCP process is not running")
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self.process.stdin.write(json.dumps(msg) + "\n")
        self.process.stdin.flush()

    def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        req_id = self._next_id()
        msg = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params
        }

        if self.http_mode:
            import urllib.request
            req = urllib.request.Request(
                self.http_url,
                data=json.dumps(msg).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.http_token}"
                }
            )
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                data = resp.read().decode("utf-8")
                res = json.loads(data)
                if "error" in res:
                    raise RuntimeError(f"MCP HTTP Error: {res['error']}")
                return res.get("result", {})

        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Drift MCP process is not running")

        self.process.stdin.write(json.dumps(msg) + "\n")
        self.process.stdin.flush()

        line = self.process.stdout.readline()
        if not line:
            stderr_out = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Drift process closed pipe unexpectedly. Stderr: {stderr_out}")

        res = json.loads(line)
        if "error" in res:
            raise RuntimeError(f"MCP RPC Error: {res['error']}")
        return res.get("result", {})

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Calls an MCP tool on Drift."""
        res = self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        content = res.get("content", [])
        if content and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except json.JSONDecodeError:
                return {"text": content[0]["text"]}
        return res

    def apply(self, ops: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executes operations via Drift's apply tool."""
        return self.call_tool("apply", {"ops": ops})

    def inspect(self, clips: bool = True, detail: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Inspects timeline state."""
        return self.call_tool("inspect", {"clips": clips, "detail": detail, "verbose": verbose})

    # --- Native TTS & Voice operations ---

    def local_tts_status(self, warm_up: bool = False) -> Dict[str, Any]:
        """Checks local TTS status and available languages."""
        args = {"warm_up": warm_up} if warm_up else {}
        res = self.apply([{"tool": "local_tts_status", "args": args}])
        done = res.get("done", [])
        if done and "result" in done[0]:
            return done[0]["result"]
        return res

    def list_local_voices(self) -> List[Dict[str, Any]]:
        """Returns the list of voices available for local Chatterbox."""
        res = self.apply([{"tool": "list_local_voices", "args": {}}])
        done = res.get("done", [])
        if done and "result" in done[0]:
            return done[0]["result"].get("voices", [])
        return []

    def tts_generate(
        self,
        text: str,
        voice: str = "default",
        language: str = "pt",
        exaggeration: float = 0.5,
        provider: str = "local",
        place: bool = False
    ) -> Dict[str, Any]:
        """
        Starts an asynchronous voice generation job using Chatterbox local TTS.
        Returns the job dict containing job_id.
        """
        args = {
            "text": text,
            "voice": voice,
            "language": language,
            "exaggeration": max(0.25, min(2.0, exaggeration)),
            "provider": provider,
            "place": place
        }
        res = self.apply([{"tool": "tts_generate", "args": args}])
        done = res.get("done", [])
        if done and "result" in done[0]:
            return done[0]["result"]
        return res

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Polls the status of an ongoing background job."""
        res = self.apply([{"tool": "get_job", "args": {"id": job_id}}])
        done = res.get("done", [])
        if done and "result" in done[0]:
            return done[0]["result"]
        return res

    def add_voice(self, name: str, audio_path: str) -> Dict[str, Any]:
        """
        Clones a voice from a 3-20 second audio sample.
        Returns job dict containing job_id.
        """
        args = {"name": name, "path": str(Path(audio_path).resolve())}
        res = self.apply([{"tool": "add_voice", "args": args}])
        done = res.get("done", [])
        if done and "result" in done[0]:
            return done[0]["result"]
        return res

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancels a running background job."""
        res = self.apply([{"tool": "cancel_job", "args": {"id": job_id}}])
        done = res.get("done", [])
        if done and "result" in done[0]:
            return done[0]["result"]
        return res

