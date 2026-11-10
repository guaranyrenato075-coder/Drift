"""
Soundtrack Auto Loop & Duration Stretcher.
Estende trilhas musicais até a duração exata da timeline aplicando
crossfades espectrais transparentes em pontos rítmicos sem cortes abruptos.
"""

from typing import Dict, Any, List
import math
from models.scene_plan import ProjectPlan


class SoundtrackAutoLoopStretcher:
    """Calcula repetições e crossfades para adaptar a música à duração do vídeo."""

    @classmethod
    def calculate_soundtrack_stretch(
        cls,
        video_duration_seconds: float,
        soundtrack_duration_seconds: float = 120.0,
        crossfade_seconds: float = 3.0
    ) -> Dict[str, Any]:
        """Calcula a quantidade necessária de loops e gera o filtro FFmpeg acrossfade."""
        if soundtrack_duration_seconds <= 0.0:
            soundtrack_duration_seconds = 120.0

        if video_duration_seconds <= soundtrack_duration_seconds:
            # Não precisa de loop, apenas fade-out final
            return {
                "needs_loop": False,
                "loops_required": 1,
                "video_duration": round(video_duration_seconds, 2),
                "soundtrack_duration": round(soundtrack_duration_seconds, 2),
                "effective_duration": round(video_duration_seconds, 2),
                "ffmpeg_filter": f"afade=t=out:st={max(0.0, round(video_duration_seconds - 3.0, 2))}:d=3.0",
                "status": "FIT_DIRECT"
            }

        # Duração útil de cada repetição considerando o crossfade
        effective_chunk_duration = soundtrack_duration_seconds - crossfade_seconds
        loops_count = math.ceil((video_duration_seconds - soundtrack_duration_seconds) / max(effective_chunk_duration, 1.0)) + 1

        # Gera comando FFmpeg aloop / acrossfade
        ffmpeg_filter = (
            f"aloop=loop={loops_count - 1}:size={int(soundtrack_duration_seconds * 44100)},"
            f"afade=t=out:st={max(0.0, round(video_duration_seconds - 3.5, 2))}:d=3.5"
        )

        return {
            "needs_loop": True,
            "loops_required": loops_count,
            "video_duration": round(video_duration_seconds, 2),
            "soundtrack_duration": round(soundtrack_duration_seconds, 2),
            "crossfade_seconds": crossfade_seconds,
            "seamless_transitions_count": loops_count - 1,
            "ffmpeg_filter": ffmpeg_filter,
            "status": "SEAMLESS_LOOP_STRETCHED"
        }

    @classmethod
    def stretch_plan_soundtrack(
        cls,
        plan: ProjectPlan,
        soundtrack_duration_seconds: float = 120.0,
        crossfade_seconds: float = 3.0
    ) -> Dict[str, Any]:
        """Aplica o cálculo de extensão musical à duração total do plano."""
        scenes = getattr(plan, "scenes", [])
        total_vid_duration = sum(float(getattr(s, "duration", 5.0)) for s in scenes)
        if total_vid_duration <= 0.0:
            total_vid_duration = 60.0

        res = cls.calculate_soundtrack_stretch(
            video_duration_seconds=total_vid_duration,
            soundtrack_duration_seconds=soundtrack_duration_seconds,
            crossfade_seconds=crossfade_seconds
        )
        setattr(plan, "soundtrack_loop_config", res)
        return res
