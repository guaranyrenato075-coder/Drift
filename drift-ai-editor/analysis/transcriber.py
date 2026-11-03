from typing import Dict, Any, List, Optional
from pathlib import Path
from editing.drift_mcp_client import DriftMcpClient

class AudioTranscriber:
    """
    Transcribes audio/video files using Drift's native Whisper model over MCP.
    """

    def __init__(self, mcp_client: DriftMcpClient):
        self.client = mcp_client

    def transcribe_file(self, media_path: Path | str, language: str = "pt") -> Dict[str, Any]:
        """
        Uses Drift's transcribe op to generate word-level timestamped transcriptions.
        """
        path_str = str(Path(media_path).resolve())
        # First ensure media is in bin
        import_res = self.client.apply([{"tool": "import_media", "args": {"paths": [path_str]}}])
        done = import_res.get("done", [])
        if not done or "result" not in done[0]:
            return {"ok": False, "error": f"Falha importando arquivo para transcrição: {import_res}"}

        assets = done[0]["result"].get("assets", [])
        if not assets:
            return {"ok": False, "error": "Nenhum asset retornado para o arquivo"}

        asset_id = assets[0]["id"]
        res = self.client.apply([{
            "tool": "transcribe",
            "args": {
                "asset": asset_id,
                "language": language
            }
        }])
        return res

