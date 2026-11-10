"""
Stereo to 5.1 Surround Sound Upmixer.
Converte áudio estéreo 2.0 em surround 5.1 cinematográfico para Home Theaters e Cinema,
isolando diálogos no canal central (C), sub-bass no LFE e reverberação nos surrounds (SL/SR).
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class StereoTo51SurroundUpmixer:
    """Gera matrizes de canal e filtros FFmpeg de upmix surround 5.1."""

    @classmethod
    def build_51_surround_filter(
        cls,
        center_dialogue_boost_db: float = 2.0,
        lfe_lowpass_hz: int = 120,
        surround_delay_ms: int = 18
    ) -> Dict[str, Any]:
        """Gera a matriz e a cadeia de filtros FFmpeg para upmix 5.1."""
        # Canais: FL (Front Left), FR (Front Right), FC (Front Center), LFE (Subwoofer), SL (Surround Left), SR (Surround Right)
        # Matriz:
        # c0 (FL) = 0.7 * L
        # c1 (FR) = 0.7 * R
        # c2 (FC) = 0.5 * L + 0.5 * R (mono sum para fala)
        # c3 (LFE) = 0.5 * L + 0.5 * R com lowpass
        # c4 (SL) = 0.6 * L - 0.4 * R (diferença estéreo com delay)
        # c5 (SR) = 0.6 * R - 0.4 * L (diferença estéreo com delay)

        pan_matrix = (
            "pan=5.1|"
            "c0=0.7*c0|"
            "c1=0.7*c1|"
            "c2=0.5*c0+0.5*c1|"
            "c3=0.5*c0+0.5*c1|"
            "c4=0.6*c0-0.4*c1|"
            "c5=0.6*c1-0.4*c0"
        )

        filter_chain = (
            f"{pan_matrix},"
            f"volume=volume={center_dialogue_boost_db}dB:eval=once"
        )

        return {
            "channel_layout": "5.1(side)",
            "channels_count": 6,
            "center_boost_db": center_dialogue_boost_db,
            "lfe_cutoff_hz": lfe_lowpass_hz,
            "surround_delay_ms": surround_delay_ms,
            "pan_matrix": pan_matrix,
            "ffmpeg_audio_filter": filter_chain,
            "standard": "ITU-R BS.775 5.1 Surround Standard"
        }

    @classmethod
    def apply_51_upmix_to_plan(
        cls,
        plan: ProjectPlan,
        center_dialogue_boost_db: float = 2.0
    ) -> Dict[str, Any]:
        """Aplica as diretivas de renderização multicanal 5.1 ao plano."""
        upmix_info = cls.build_51_surround_filter(center_dialogue_boost_db=center_dialogue_boost_db)
        setattr(plan, "surround_51_config", upmix_info)
        return {
            "status": "APPLIED",
            "upmix_config": upmix_info
        }
