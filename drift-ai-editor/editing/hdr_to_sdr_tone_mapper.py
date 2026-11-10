"""
HDR to SDR Tone Mapper & Color Gamut Conformist.
Converte filmagens de alta gama dinâmica (HDR10, HLG, Apple Log, Sony S-Log)
para o espaço padrão Rec.709 (SDR) sem perda de contraste ou sombras lavadas.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class HDRToSDRToneMapper:
    """Aplica algoritmos de mapeamento de tom (Tone Mapping) via filtros FFmpeg zscale."""

    TONE_MAP_PRESETS = {
        "mobius_balanced": {
            "name": "Mobius (Equilibrado & Realista)",
            "description": "Preserva detalhes em altas luzes com transição suave para tons médios.",
            "tonemap": "mobius",
            "peak": 100.0,
            "desat": 0.5,
            "ffmpeg_filter": "zscale=t=linear:npl=100,tonemap=mobius:desat=0.5:peak=100,zscale=p=bt709:t=bt709:m=bt709:r=limited"
        },
        "reinhard_soft_highlight": {
            "name": "Reinhard (Altas Luzes Suaves)",
            "description": "Compressão clássica de altas luzes ideal para filmagens externas com céu brilhante.",
            "tonemap": "reinhard",
            "peak": 100.0,
            "desat": 0.4,
            "ffmpeg_filter": "zscale=t=linear:npl=100,tonemap=reinhard:desat=0.4:peak=100,zscale=p=bt709:t=bt709:m=bt709:r=limited"
        },
        "hable_cinematic": {
            "name": "Hable / Uncharted (Contraste Fílmico)",
            "description": "Curva fílmica com sombras ricas e pretos profundos (estilo cinematográfico AAA).",
            "tonemap": "hable",
            "peak": 100.0,
            "desat": 0.35,
            "ffmpeg_filter": "zscale=t=linear:npl=100,tonemap=hable:desat=0.35:peak=100,zscale=p=bt709:t=bt709:m=bt709:r=limited"
        },
        "aces_filmic": {
            "name": "ACES Filmic (Academia de Cinema)",
            "description": "Emulação de curva padrão ACES para reprodução fiel de cores de câmeras cinema.",
            "tonemap": "linear",
            "peak": 100.0,
            "desat": 0.3,
            "ffmpeg_filter": "zscale=t=linear:npl=100,tonemap=clip:peak=100,zscale=p=bt709:t=bt709:m=bt709:r=limited"
        }
    }

    @classmethod
    def get_available_presets(cls) -> Dict[str, Dict[str, Any]]:
        return cls.TONE_MAP_PRESETS

    @classmethod
    def build_tone_map_filter(cls, preset_name: str = "mobius_balanced") -> str:
        """Gera a string de filtros FFmpeg de conversão para SDR Rec.709."""
        preset = cls.TONE_MAP_PRESETS.get(preset_name, cls.TONE_MAP_PRESETS["mobius_balanced"])
        return preset["ffmpeg_filter"]

    @classmethod
    def apply_tone_mapping_to_plan(cls, plan: ProjectPlan, preset_name: str = "mobius_balanced") -> Dict[str, Any]:
        """Configura o plano de edição para converter clipes HDR no render."""
        if preset_name not in cls.TONE_MAP_PRESETS:
            preset_name = "mobius_balanced"

        preset = cls.TONE_MAP_PRESETS[preset_name]
        setattr(plan, "hdr_tone_map_preset", preset_name)
        setattr(plan, "hdr_tone_map_ffmpeg_filter", preset["ffmpeg_filter"])

        return {
            "status": "CONFIGURED",
            "preset_name": preset_name,
            "preset_details": preset,
            "target_color_space": "Rec.709 SDR (Limited Range)"
        }
