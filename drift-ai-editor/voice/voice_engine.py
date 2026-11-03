import time
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from models.scene_plan import Scene, SceneState
from voice.base import BaseVoiceEngine
from editing.drift_mcp_client import DriftMcpClient

class DriftChatterboxEngine(BaseVoiceEngine):
    """
    Voice engine implementation using Drift's native Chatterbox local TTS over MCP.
    """

    def __init__(self, mcp_client: DriftMcpClient):
        self.client = mcp_client

    def check_status(self, warm_up: bool = False) -> Dict[str, Any]:
        """
        Queries Drift for local TTS availability and supported languages.
        """
        status = self.client.local_tts_status(warm_up=warm_up)
        return {
            "ok": status.get("ok", False),
            "available": status.get("available", False),
            "addon_id": status.get("addon_id", "tts-model"),
            "languages": status.get("languages", []),
            "last_voice": status.get("last_voice", "default"),
            "last_exaggeration": status.get("last_exaggeration", 0.5),
            "model_loaded": status.get("model_loaded", False),
            "loading": status.get("loading", False)
        }

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        Queries Drift for local voices.
        """
        return self.client.list_local_voices()

    def generate_scene(self, scene: Scene, timeout_sec: float = 120.0) -> Scene:
        """
        Generates TTS audio for a single scene using Drift's Chatterbox.
        Polls until completion and updates the scene's real duration and audio path.
        """
        if not scene.narration_text.strip():
            scene.state = SceneState.READY
            scene.duration = max(scene.duration, 2.0)
            return scene

        scene.state = SceneState.VOICE_GENERATING
        scene.error_message = None

        # Call tts_generate
        gen_res = self.client.tts_generate(
            text=scene.narration_text,
            voice=scene.voice_id or "default",
            language=scene.language or "pt",
            exaggeration=scene.exaggeration or 0.5,
            provider="local",
            place=False
        )

        job_id = gen_res.get("job_id")
        if not job_id:
            # Check if result was returned immediately (e.g. cached)
            if "path" in gen_res or "duration" in gen_res:
                scene.audio_path = gen_res.get("path")
                scene.duration = float(gen_res.get("duration", 3.0))
                scene.audio_duration = scene.duration
                scene.state = SceneState.READY
                return scene
            else:
                scene.state = SceneState.ERROR
                scene.error_message = f"Falha ao iniciar geração TTS: {gen_res}"
                return scene

        scene.audio_job_id = job_id

        # Poll job status until active is false
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            job = self.client.get_job(job_id)
            active = job.get("active", True)
            
            if active:
                time.sleep(1.0)
                continue

            # Job is finished (active is False)
            if job.get("error"):
                err = job.get("error")
                err_msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                scene.state = SceneState.ERROR
                scene.error_message = f"Erro na geração de voz: {err_msg}"
                return scene

            result = job.get("result", {})
            if not isinstance(result, dict):
                result = {}

            scene.audio_path = result.get("path") or job.get("path")
            dur = float(result.get("duration") or job.get("duration") or 0.0)
            if dur > 0:
                scene.duration = dur
                scene.audio_duration = dur
            else:
                scene.duration = max(scene.duration, 3.0)
                scene.audio_duration = scene.duration

            scene.state = SceneState.READY
            return scene

        scene.state = SceneState.ERROR
        scene.error_message = f"Tempo limite excedido ({timeout_sec}s) gerando voz para a cena {scene.order}"
        return scene

    def generate_sample(self, text: str, voice_id: str, language: str, exaggeration: float = 0.5) -> Dict[str, Any]:
        """
        Generates a quick sample audio for auditioning voices.
        """
        temp_scene = Scene(
            order=0,
            narration_text=text,
            voice_id=voice_id,
            language=language,
            exaggeration=exaggeration
        )
        result_scene = self.generate_scene(temp_scene, timeout_sec=60.0)
        return {
            "ok": result_scene.state == SceneState.READY,
            "audio_path": result_scene.audio_path,
            "duration": result_scene.duration,
            "error": result_scene.error_message
        }

    def clone_voice(self, name: str, audio_path: str, timeout_sec: float = 60.0) -> Dict[str, Any]:
        """
        Clones a new local voice from an audio sample file (3-20s clean speech).
        """
        res = self.client.add_voice(name, audio_path)
        job_id = res.get("job_id")
        if not job_id:
            return {"ok": False, "error": f"Falha ao iniciar clonagem: {res}"}

        start = time.time()
        while time.time() - start < timeout_sec:
            job = self.client.get_job(job_id)
            if job.get("active") is False:
                if job.get("error"):
                    return {"ok": False, "error": job.get("error")}
                return {"ok": True, "voice": job.get("result", {}).get("voice", name)}
            time.sleep(1.0)

        return {"ok": False, "error": "Tempo limite excedido na clonagem de voz"}

    def process_scenes_batch(self, scenes: List[Scene], on_progress=None) -> List[Scene]:
        """
        Processes voice generation for multiple scenes sequentially
        (Chatterbox runs one local job at a time).
        """
        for idx, scene in enumerate(scenes):
            if scene.state != SceneState.READY or not scene.audio_path:
                self.generate_scene(scene)
            if on_progress:
                on_progress(idx + 1, len(scenes), scene)
        return scenes

