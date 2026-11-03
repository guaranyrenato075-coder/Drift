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

    def start(self):
        """Starts the drift.exe process with --headless and --mcp-stdio."""
        if self.process and self.process.poll() is None:
            return

        if not self.drift_exe.exists():
            raise FileNotFoundError(f"Drift executable not found at {self.drift_exe}")

        self.process = subprocess.Popen(
            [str(self.drift_exe), "--headless", "--mcp-stdio"],
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
        """Gracefully terminates the Drift process."""
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
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Drift MCP process is not running")

        req_id = self._next_id()
        msg = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params
        }
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

