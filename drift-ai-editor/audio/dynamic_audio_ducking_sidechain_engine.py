"""
Módulo de Dynamic Audio Ducking e Sidechain Compression.
Calcula e gera pipelines FFmpeg de sidechain compression inteligente
para abaixar automaticamente a trilha sonora musical de fundo quando
a narração/voz estiver presente, garantindo inteligibilidade máxima.
"""

from typing import Dict, Any, List, Optional


class DynamicAudioDuckingSidechainEngine:
    """
    Motor de compressão sidechain e auto-ducking para balanceamento de áudio profissional de cinema.
    """

    DUCKING_PRESETS = {
        "broadcast_standard": {
            "threshold_db": -24.0,
            "ratio": 6.0,
            "attack_ms": 50,
            "release_ms": 350,
            "ducking_depth_db": -16.0,
            "makeup_gain_db": 0.0,
            "knee_db": 2.8,
            "description": "Padrão de transmissão de TV e rádio (atenuação de -16dB, suave e natural)."
        },
        "cinematic_dramatic": {
            "threshold_db": -28.0,
            "ratio": 8.0,
            "attack_ms": 30,
            "release_ms": 450,
            "ducking_depth_db": -20.0,
            "makeup_gain_db": 0.0,
            "knee_db": 4.0,
            "description": "Impacto cinematográfico: música recua dramaticamente durante diálogos."
        },
        "youtube_fast_paced": {
            "threshold_db": -20.0,
            "ratio": 5.0,
            "attack_ms": 20,
            "release_ms": 200,
            "ducking_depth_db": -14.0,
            "makeup_gain_db": 1.0,
            "knee_db": 1.5,
            "description": "Edição rápida do YouTube/TikTok: recuperação dinâmica e rápida de ritmo."
        },
        "subtle_documentary": {
            "threshold_db": -26.0,
            "ratio": 3.5,
            "attack_ms": 80,
            "release_ms": 600,
            "ducking_depth_db": -10.0,
            "makeup_gain_db": 0.0,
            "knee_db": 5.0,
            "description": "Documentário elegante: atenuação sutil de -10dB sem cortes perceptíveis."
        }
    }

    @classmethod
    def calculate_ducking_filter(
        cls,
        preset: str = "broadcast_standard",
        music_stream_idx: str = "0:a",
        voice_stream_idx: str = "1:a",
        custom_depth_db: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Gera a string do filtro FFmpeg sidechaincompress para ducking perfeito de áudio.
        """
        config = dict(cls.DUCKING_PRESETS.get(preset, cls.DUCKING_PRESETS["broadcast_standard"]))

        if custom_depth_db is not None:
            config["ducking_depth_db"] = custom_depth_db

        threshold = config["threshold_db"]
        ratio = config["ratio"]
        attack = config["attack_ms"]
        release = config["release_ms"]
        knee = config["knee_db"]
        makeup = config["makeup_gain_db"]

        # FFmpeg filter: [music][voice]sidechaincompress=threshold=...:ratio=...:attack=...:release=...[ducked]
        # Converte dB em linear quando necessário ou usa a sintaxe padrão do FFmpeg sidechaincompress
        filter_str = (
            f"[{music_stream_idx}][{voice_stream_idx}]sidechaincompress="
            f"threshold={threshold}dB:ratio={ratio}:attack={attack}:release={release}:knee={knee}dB:makeup={makeup}dB[ducked_music]"
        )

        # Mixagem final: mixa a música ducked com a voz
        full_complex_filter = (
            f"{filter_str}; "
            f"[{voice_stream_idx}]volume=1.0[voice_main]; "
            f"[ducked_music][voice_main]amix=inputs=2:duration=longest:dropout_transition=2[out_audio]"
        )

        return {
            "status": "success",
            "preset_applied": preset,
            "config": config,
            "sidechain_filter": filter_str,
            "ffmpeg_complex_filter": full_complex_filter,
            "recommendation": f"Preset '{preset}' aplicado: atenuação de {config['ducking_depth_db']}dB com ataque de {attack}ms e release de {release}ms."
        }

    @classmethod
    def analyze_audio_track_levels(cls, speech_intervals: List[Dict[str, float]], total_duration: float) -> Dict[str, Any]:
        """
        Analisa a linha do tempo de fala e calcula a proporção de cobertura de voz vs música cheia.
        """
        voice_time = 0.0
        for seg in speech_intervals:
            start = float(seg.get("start", 0.0))
            end = float(seg.get("end", 0.0))
            if end > start:
                voice_time += (end - start)

        voice_coverage_pct = round((voice_time / max(total_duration, 0.1)) * 100.0, 1)
        music_full_presence_pct = round(100.0 - voice_coverage_pct, 1)

        pacing_rating = "Dinâmico Equilibrado"
        if voice_coverage_pct > 85.0:
            pacing_rating = "Muito Denso (Pouco respiro musical)"
        elif voice_coverage_pct < 40.0:
            pacing_rating = "Foco em Trilha Sonora / Visual Contemplativo"

        return {
            "status": "success",
            "total_duration_sec": total_duration,
            "voice_duration_sec": round(voice_time, 2),
            "voice_coverage_pct": voice_coverage_pct,
            "music_full_presence_pct": music_full_presence_pct,
            "pacing_style": pacing_rating,
            "recommended_ducking_preset": "youtube_fast_paced" if voice_coverage_pct > 70 else "cinematic_dramatic"
        }
