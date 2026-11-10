"""
Dynamic Zoom Punch & Audio Sidechain Ducking Director for CutWire Drift AI.
Orchestrates micro camera punch-ins aligned with vocal emphasis and calculates mathematically exact
FFmpeg sidechain ducking filters to smoothly attenuate background music during narration.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from models.scene_plan import Scene, ProjectPlan

@dataclass
class PunchInTrigger:
    scene_order: int
    trigger_word: str
    timestamp_offset_sec: float
    zoom_level: float
    duration_sec: float
    narrative_reason: str

class DynamicZoomPunchAudioDuckingDirector:
    """
    Directs audio sidechain ducking and vocal emphasis zoom punch-ins.
    """

    EMPHASIS_KEYWORDS = {
        "nunca", "jamais", "segredo", "perigo", "verdade", "choque", "incrível",
        "atenção", "olhe", "veja", "destruição", "morte", "revelou", "confronto",
        "urgente", "absurdo", "inacreditável", "revelação", "cuidado", "fatal"
    }

    @classmethod
    def calculate_sidechain_ducking_filter(
        cls,
        duck_db: float = -14.0,
        attack_ms: float = 25.0,
        release_ms: float = 350.0,
        music_volume: float = 0.20
    ) -> str:
        """
        Builds FFmpeg filter_complex snippet for automated sidechain ducking.
        Music is attenuated whenever narration audio amplitude crosses threshold.
        """
        # sidechaincompress: threshold=0.125 (-18dB), ratio=4, attack=attack_ms, release=release_ms
        duck_filter = (
            f"[1:a]volume={music_volume:.2f}[bgm_vol];"
            f"[bgm_vol][0:a]sidechaincompress=threshold=0.10:ratio=5:"
            f"attack={attack_ms}:release={release_ms}:makeup=1.0[bgm_ducked];"
            f"[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[out_audio]"
        )
        return duck_filter

    @classmethod
    def detect_vocal_punch_in_triggers(cls, plan: ProjectPlan) -> List[PunchInTrigger]:
        """
        Scans scenes narration to detect high-impact words and calculates
        micro punch-in events (0.35s camera punch to 1.12x) to capture viewer attention.
        """
        triggers: List[PunchInTrigger] = []

        for scene in plan.scenes:
            text = (scene.narration_text or "").lower()
            words = re.findall(r'\b[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ]+\b', text)
            total_words = len(words)
            dur = max(scene.duration or 3.0, 1.0)

            for idx, w in enumerate(words):
                if w in cls.EMPHASIS_KEYWORDS:
                    # Estimate word timestamp proportionally within scene duration
                    approx_offset = (idx / max(total_words, 1)) * dur
                    triggers.append(PunchInTrigger(
                        scene_order=scene.order,
                        trigger_word=w.upper(),
                        timestamp_offset_sec=round(approx_offset, 2),
                        zoom_level=1.12,
                        duration_sec=0.35,
                        narrative_reason=f"Ênfase dramática detectada na palavra '{w.upper()}'."
                    ))

        return triggers

    @classmethod
    def generate_punchin_zoom_filter(
        cls,
        triggers: List[PunchInTrigger],
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Generates FFmpeg zoompan / crop expression that triggers sudden micro punch-ins.
        """
        if not triggers:
            return ""

        # Build conditional expressions
        conditions = []
        for t in triggers:
            start_t = t.timestamp_offset_sec
            end_t = start_t + t.duration_sec
            conditions.append(f"between(t,{start_t:.2f},{end_t:.2f})*0.12")

        sum_expr = "+".join(conditions)
        filter_str = (
            f"scale=2*iw:-1,zoompan=z='1.00+({sum_expr})':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}"
        )
        return filter_str

    @classmethod
    def plan_ducking_and_punchins(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """
        Generates unified ducking and punch-in execution plan for the project.
        """
        triggers = cls.detect_vocal_punch_in_triggers(plan)
        duck_filter = cls.calculate_sidechain_ducking_filter()
        punch_filter = cls.generate_punchin_zoom_filter(triggers, plan.config.width, plan.config.height)

        return {
            "project_id": plan.project_id,
            "total_punch_triggers": len(triggers),
            "sidechain_ducking_filter": duck_filter,
            "punch_in_filter": punch_filter,
            "triggers": [t.__dict__ for t in triggers]
        }
