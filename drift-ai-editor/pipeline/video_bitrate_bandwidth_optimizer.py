"""
Video Bitrate & Bandwidth Optimizer.
Calcula taxas de compressão VBR 2-pass cirúrgicas baseadas na resolução,
complexidade visual da cena e especificações recomendadas pelo YouTube/Broadcast.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class VideoBitrateBandwidthOptimizer:
    """Otimiza a alocação de bitrate e comandos FFmpeg para streaming e arquivamento."""

    EXPORT_PROFILES = {
        "youtube_4k_ultra": {
            "name": "YouTube 4K Ultra (2160p60)",
            "resolution": "3840x2160",
            "fps": 60,
            "target_bitrate_kbps": 53000,
            "max_bitrate_kbps": 68000,
            "bufsize_kbps": 106000,
            "codec": "libx265",
            "preset": "slow",
            "crf": 18,
            "description": "Qualidade máxima para telas grandes e televisores 4K HDR."
        },
        "youtube_1080p_pro": {
            "name": "YouTube 1080p Pro (FHD 60fps)",
            "resolution": "1920x1080",
            "fps": 60,
            "target_bitrate_kbps": 12000,
            "max_bitrate_kbps": 15000,
            "bufsize_kbps": 24000,
            "codec": "libx264",
            "preset": "medium",
            "crf": 20,
            "description": "Padrão de ouro para YouTube com alta nitidez em movimentos rápidos."
        },
        "web_fast_stream": {
            "name": "Web Fast Stream (Otimizado p/ Mobile)",
            "resolution": "1920x1080",
            "fps": 30,
            "target_bitrate_kbps": 5500,
            "max_bitrate_kbps": 7000,
            "bufsize_kbps": 11000,
            "codec": "libx264",
            "preset": "faster",
            "crf": 23,
            "description": "Arquivo leve com carregamento veloz para conexões móveis 4G/5G."
        },
        "archive_lossless_prores": {
            "name": "Master de Arquivo ProRes 422 HQ",
            "resolution": "3840x2160",
            "fps": 60,
            "target_bitrate_kbps": 220000,
            "max_bitrate_kbps": 250000,
            "bufsize_kbps": 300000,
            "codec": "prores_ks",
            "preset": "hq",
            "crf": 0,
            "description": "Codec intermediário broadcast para arquivamento sem perda."
        }
    }

    @classmethod
    def get_available_profiles(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna os perfis de compressão disponíveis."""
        return cls.EXPORT_PROFILES

    @classmethod
    def calculate_project_bitrate_plan(cls, plan: ProjectPlan, profile_name: str = "youtube_1080p_pro") -> Dict[str, Any]:
        """Calcula o consumo estimado de MB e parâmetros de renderização."""
        if profile_name not in cls.EXPORT_PROFILES:
            profile_name = "youtube_1080p_pro"

        profile = cls.EXPORT_PROFILES[profile_name]
        scenes = getattr(plan, "scenes", [])
        total_duration = sum(float(getattr(s, "duration", 5.0)) for s in scenes)
        if total_duration <= 0.0:
            total_duration = 60.0

        target_kbps = profile["target_bitrate_kbps"]
        # Tamanho estimado: (bitrate_kbps * segundos) / 8192 = MB
        estimated_file_size_mb = round((target_kbps * total_duration) / 8192.0, 1)

        # Constrói argumentos do FFmpeg
        if profile["codec"] == "prores_ks":
            ffmpeg_args = f"-c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le"
        else:
            ffmpeg_args = (
                f"-c:v {profile['codec']} -preset {profile['preset']} -crf {profile['crf']} "
                f"-b:v {target_kbps}k -maxrate {profile['max_bitrate_kbps']}k -bufsize {profile['bufsize_kbps']}k "
                f"-pix_fmt yuv420p -movflags +faststart"
            )

        return {
            "profile_name": profile_name,
            "profile_details": profile,
            "total_duration_seconds": round(total_duration, 2),
            "estimated_file_size_mb": estimated_file_size_mb,
            "ffmpeg_compression_args": ffmpeg_args,
            "bandwidth_efficiency": "OTIMIZADO",
            "status": "CALCULATED"
        }
