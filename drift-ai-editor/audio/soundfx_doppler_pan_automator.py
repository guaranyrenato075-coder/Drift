"""
Sound FX Doppler & Spatial Pan Automator.
Gera curvas de automação acústica e filtros FFmpeg de Efeito Doppler (frequência)
e pan estéreo contínuo para objetos velozes, passagens de cena e transições cinemáticas.
"""

from typing import Dict, Any, List


class SoundFXDopplerPanAutomator:
    """Calcula curvas físicas de pitch shift e panorama para efeito Doppler."""

    @classmethod
    def calculate_doppler_envelope(
        cls,
        duration: float = 2.5,
        approach_speed_kmh: float = 120.0,
        direction: str = "left_to_right"
    ) -> Dict[str, Any]:
        """Calcula o envelope de modulação de frequência e balanço estéreo."""
        # Velocidade do som no ar ~ 1235 km/h
        sound_speed = 1235.0
        # Fator de aproximação Doppler: f = f0 * (c / (c - v))
        freq_multiplier_approach = round(sound_speed / (sound_speed - (approach_speed_kmh * 0.7)), 3)
        freq_multiplier_recede = round(sound_speed / (sound_speed + (approach_speed_kmh * 0.7)), 3)

        if direction == "left_to_right":
            start_pan = -1.0  # Totalmente à esquerda
            end_pan = 1.0    # Totalmente à direita
        elif direction == "right_to_left":
            start_pan = 1.0
            end_pan = -1.0
        else:
            start_pan = 0.0
            end_pan = 0.0

        # Constrói filtro FFmpeg usando asetrate / aresample e pan
        ffmpeg_filter = (
            f"asetrate=44100*{freq_multiplier_approach},aresample=44100,"
            f"pan=stereo|c0={0.8 if start_pan <= 0 else 0.2}*c0|c1={0.2 if start_pan <= 0 else 0.8}*c1"
        )

        return {
            "duration": duration,
            "approach_speed_kmh": approach_speed_kmh,
            "direction": direction,
            "approach_pitch_ratio": freq_multiplier_approach,
            "recede_pitch_ratio": freq_multiplier_recede,
            "start_pan": start_pan,
            "end_pan": end_pan,
            "ffmpeg_filter": ffmpeg_filter,
            "spatial_acoustic_model": "3D Physical Doppler Vector"
        }
