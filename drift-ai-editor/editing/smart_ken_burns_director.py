"""
Smart Ken Burns Camera Motion Director for CutWire Drift AI.
Orchestrates context-aware camera vectors (Slow Face Zoom-In, Panoramic Horizontal Pan,
Wide Pull-Out, and Dramatic Fast Push-In) with mathematically exact FFmpeg zoompan filter expressions.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from models.scene_plan import Scene, ProjectPlan

@dataclass
class CameraMotionConfig:
    scene_order: int
    motion_type: str  # "slow_zoom_in", "pan_horizontal", "slow_pull_out", "fast_push_in"
    narrative_reason: str
    zoom_range: str
    ffmpeg_filter: str

class SmartSceneKenBurnsDirector:
    """
    Directs dynamic camera movement algorithms tailored to visual subjects.
    """

    PORTRAIT_KEYWORDS = {"rosto", "face", "estátua", "busto", "olhos", "homem", "mulher", "pessoa", "imperador", "filósofo", "retrato"}
    WIDE_KEYWORDS = {"mapa", "galáxia", "nebulosa", "universo", "planeta", "paisagem", "cidade", "horizonte", "deserto", "oceano", "montanha"}
    CLIMAX_KEYWORDS = {"choque", "perigo", "destruição", "morte", "explosão", "revelou", "confronto", "urgente"}

    @classmethod
    def evaluate_scene_motion(cls, scene: Scene, width: int = 1920, height: int = 1080, fps: float = 30.0) -> CameraMotionConfig:
        combined = (scene.narration_text + " " + scene.visual_description + " " + " ".join(scene.english_keywords or [])).lower()
        words = set(re.findall(r'\b\w+\b', combined))
        dur = max(scene.duration or 3.0, 1.0)
        total_frames = int(dur * fps)

        # 1. Climax -> Fast push-in
        if words.intersection(cls.CLIMAX_KEYWORDS):
            motion_type = "fast_push_in"
            reason = "Momento de clímax ou revelação: zoom rápido para intensificar o impacto dramático."
            zoom_range = "1.00x ➔ 1.35x"
            # Fast zoom
            filt = f"zoompan=z='min(zoom+0.0035,1.35)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        # 2. Portrait / Statue -> Slow face zoom-in
        elif words.intersection(cls.PORTRAIT_KEYWORDS):
            motion_type = "slow_zoom_in"
            reason = "Figura humana ou estátua clássica: aproximação sutil nos olhos/expressão facial."
            zoom_range = "1.00x ➔ 1.25x"
            filt = f"zoompan=z='min(zoom+0.0015,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/3-(ih/zoom/3)':s={width}x{height}:fps={fps}"

        # 3. Wide landscape / Galaxy / Map -> Horizontal pan or pull-out
        elif words.intersection(cls.WIDE_KEYWORDS):
            if scene.order % 2 == 0:
                motion_type = "pan_horizontal"
                reason = "Cenário panorâmico amplo: deslocamento horizontal da esquerda para a direita."
                zoom_range = "1.15x (Pan)"
                filt = f"zoompan=z='1.15':x='if(lte(on,1),0,x+1)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}"
            else:
                motion_type = "slow_pull_out"
                reason = "Imensidão cósmica ou geográfica: recuo de câmera revelando a escala do ambiente."
                zoom_range = "1.25x ➔ 1.00x"
                filt = f"zoompan=z='if(lte(zoom,1.0),1.25,max(1.001,zoom-0.0015))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        # 4. Default gentle zoom-in
        else:
            motion_type = "gentle_zoom_in"
            reason = "Movimento suave e elegante para conferir vida a imagens estáticas."
            zoom_range = "1.00x ➔ 1.18x"
            filt = f"zoompan=z='min(zoom+0.0012,1.18)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

        return CameraMotionConfig(
            scene_order=scene.order,
            motion_type=motion_type,
            narrative_reason=reason,
            zoom_range=zoom_range,
            ffmpeg_filter=filt
        )

    @classmethod
    def generate_plan_camera_manifest(cls, plan: ProjectPlan) -> Dict[str, Any]:
        w = plan.config.width
        h = plan.config.height
        fps = plan.config.fps or 30.0
        motions = [cls.evaluate_scene_motion(s, width=w, height=h, fps=fps) for s in plan.scenes]

        return {
            "project_id": plan.project_id,
            "total_scenes": len(plan.scenes),
            "camera_motions": [m.__dict__ for m in motions]
        }
