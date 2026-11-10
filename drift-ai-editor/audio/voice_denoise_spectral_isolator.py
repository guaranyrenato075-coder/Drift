"""
AI Voice Denoise & Spectral Isolator.
Aplica isolamento espectral e filtragem cirúrgica de ruído (FFT denoise,
hiss removal, highpass/lowpass e noise gate) para locuções de estúdio.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class AIVoiceDenoiseSpectralIsolator:
    """Filtra ruídos de fundo e aperfeiçoa a clareza vocal via FFmpeg."""

    DENOISE_PROFILES = {
        "studio_clean": {
            "name": "Estúdio Acústico (Neutro)",
            "description": "Remoção suave de ruído ambiente com preservação tonal e calor natural.",
            "highpass_hz": 80,
            "lowpass_hz": 12500,
            "noise_reduction_db": 12,
            "gate_threshold_db": -42.0,
            "ffmpeg_filter": "highpass=f=80,lowpass=f=12500,afftdn=nr=12:nf=-30,agate=threshold=-42dB:ratio=2:attack=20:release=150"
        },
        "podcast_crisp": {
            "name": "Podcast Moderno (Presença & Ar)",
            "description": "Acentuação das frequências de inteligibilidade vocal e corte cirúrgico de rumble.",
            "highpass_hz": 95,
            "lowpass_hz": 14000,
            "noise_reduction_db": 15,
            "gate_threshold_db": -38.0,
            "ffmpeg_filter": "highpass=f=95,lowpass=f=14000,afftdn=nr=15:nf=-28,equalizer=f=3500:t=q:w=1.2:g=2.5,agate=threshold=-38dB:ratio=2.5:attack=15:release=120"
        },
        "broadcast_warm": {
            "name": "Rádio FM / Broadcast Encorpado",
            "description": "Realce de graves de rádio, compressão quente e atenuação de sibilância.",
            "highpass_hz": 70,
            "lowpass_hz": 11000,
            "noise_reduction_db": 14,
            "gate_threshold_db": -40.0,
            "ffmpeg_filter": "highpass=f=70,lowpass=f=11000,afftdn=nr=14:nf=-32,equalizer=f=200:t=q:w=1.0:g=2.0,agate=threshold=-40dB:ratio=2:attack=25:release=200"
        },
        "aggressive_cleanup": {
            "name": "Limpeza Severa (Ruído Elétrico / Ar-Condicionado)",
            "description": "Filtro FFT agressivo e gate rígido para gravações com alto zumbido elétrico ou ventilador.",
            "highpass_hz": 110,
            "lowpass_hz": 10000,
            "noise_reduction_db": 22,
            "gate_threshold_db": -32.0,
            "ffmpeg_filter": "highpass=f=110,lowpass=f=10000,afftdn=nr=22:nf=-24,agate=threshold=-32dB:ratio=3.5:attack=10:release=90"
        }
    }

    @classmethod
    def get_available_profiles(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna os perfis de isolamento de ruído disponíveis."""
        return cls.DENOISE_PROFILES

    @classmethod
    def build_denoise_filter_command(cls, profile_name: str = "studio_clean") -> str:
        """Retorna a cadeia de filtros FFmpeg para o perfil solicitado."""
        profile = cls.DENOISE_PROFILES.get(profile_name, cls.DENOISE_PROFILES["studio_clean"])
        return profile["ffmpeg_filter"]

    @classmethod
    def apply_profile_to_project(cls, plan: ProjectPlan, profile_name: str = "studio_clean") -> Dict[str, Any]:
        """Aplica as configurações de denoise vocal ao projeto."""
        if profile_name not in cls.DENOISE_PROFILES:
            profile_name = "studio_clean"

        selected = cls.DENOISE_PROFILES[profile_name]
        setattr(plan, "voice_denoise_profile", profile_name)
        setattr(plan, "voice_denoise_ffmpeg_filter", selected["ffmpeg_filter"])

        return {
            "status": "APPLIED",
            "profile": profile_name,
            "profile_details": selected,
            "estimated_snr_gain_db": selected["noise_reduction_db"]
        }
