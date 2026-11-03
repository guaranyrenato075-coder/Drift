import time
from typing import Dict, Any, Optional
from pathlib import Path
from models.scene_plan import ProjectPlan
from editing.drift_mcp_client import DriftMcpClient

class ExportManager:
    """
    Handles rendering and exporting the timeline into MP4 files using Drift's native exporter.
    """

    def __init__(self, mcp_client: DriftMcpClient):
        self.client = mcp_client

    def export(
        self,
        output_file_path: Path | str,
        plan: ProjectPlan,
        preset: str = "medium",
        crf: int = 20,
        timeout_sec: float = 300.0
    ) -> Dict[str, Any]:
        target = Path(output_file_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        args = {
            "path": str(target),
            "video": "h264",
            "audio": "aac",
            "crf": crf,
            "fps": plan.config.fps,
            "height": plan.config.height,
            "preset": preset
        }

        res = self.client.apply([{"tool": "export_video", "args": args}])
        done = res.get("done", [])
        if not done or "result" not in done[0]:
            return {"ok": False, "error": f"Falha ao iniciar exportação: {res}"}

        # Poll export status
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            ins = self.client.inspect(clips=False, detail=True)
            export_info = ins.get("export", {})
            
            if not export_info or export_info.get("active") is False:
                # Check if target file exists and is populated
                if target.exists() and target.stat().st_size > 1024:
                    return {
                        "ok": True,
                        "output_path": str(target),
                        "size_bytes": target.stat().st_size
                    }

            if export_info.get("error"):
                return {"ok": False, "error": export_info.get("error")}

            time.sleep(1.0)

        return {"ok": False, "error": f"Tempo limite de exportação excedido ({timeout_sec}s)"}

