"""
Módulo de Pass-Through Direto de Áudio Sem Reencodificação (Lossless Audio Pass-Through).
Inspeciona metadados de codecs e parâmetros de áudio dos clipes e narrações.
Quando o stream já estiver em conformidade (ex: AAC/PCM, canais stereo, 44.1k/48k),
aplica a flag de cópia direta de fluxo (-c:a copy), poupando 100% de uso de CPU
no processamento sonoro e preservando fidelidade acústica pura bit a bit.
"""

from typing import Dict, Any, Optional


class LosslessAudioPassThroughEngine:
    """
    Motor de detecção de compatibilidade e pass-through de áudio direto (-c:a copy).
    """

    SUPPORTED_PASSTHROUGH_CODECS = {"aac", "pcm_s16le", "mp3", "flac", "opus"}
    STANDARD_SAMPLE_RATES = {44100, 48000}

    @classmethod
    def evaluate_audio_stream_compatibility(
        cls,
        codec_name: str,
        sample_rate: int,
        channels: int,
        target_container: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Avalia se a faixa de áudio pode ser copiada diretamente sem recodificação.
        """
        codec_clean = codec_name.lower().strip()
        is_codec_ok = codec_clean in cls.SUPPORTED_PASSTHROUGH_CODECS
        is_sample_rate_ok = sample_rate in cls.STANDARD_SAMPLE_RATES
        is_channels_ok = channels in (1, 2)

        # Para container MP4 padrão, AAC é o formato ideal de stream copy
        can_copy = is_codec_ok and is_sample_rate_ok and is_channels_ok
        if target_container == "mp4" and codec_clean not in ("aac", "mp3"):
            can_copy = False
            reason = f"Codec '{codec_clean}' requer transcodificação para compatibilidade com container MP4."
        elif can_copy:
            reason = f"Áudio {codec_clean.upper()} ({sample_rate}Hz, {channels}ch) 100% compatível para cópia direta."
        else:
            reason = f"Parâmetros de áudio ({codec_clean}, {sample_rate}Hz) exigem padronização normalizada."

        ffmpeg_arg = "-c:a copy" if can_copy else "-c:a aac -b:a 192k -ar 48000"
        cpu_load_reduction_pct = 100.0 if can_copy else 0.0

        return {
            "status": "success",
            "can_pass_through": can_copy,
            "detected_codec": codec_clean,
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "ffmpeg_audio_flags": ffmpeg_arg,
            "cpu_load_reduction_pct": cpu_load_reduction_pct,
            "reason": reason,
            "audio_fidelity": "Bit-Perfect Lossless (Zero Recompression)" if can_copy else "Standard 192kbps AAC"
        }
