"""
Dynamic Audio Waveform & Spectrum Visualizer for CutWire Drift AI.
Generates animated audio visualization overlays (oscilloscope waves, spectrum bars, circular rings)
for podcast episodes, archival radio broadcasts, and audio-first documentary scenes.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class WaveformStyle(str, Enum):
    OSCILLOSCOPE_LINE = "oscilloscope_line"
    FREQUENCY_BARS = "frequency_bars"
    CIRCULAR_PULSE = "circular_pulse"
    SPECTROGRAM = "spectrogram"

@dataclass
class WaveformVisualizerSpec:
    style: WaveformStyle
    width: int
    height: int
    color_hex: str
    background_transparent: bool
    ffmpeg_filter: str
    output_fps: int = 30

class AudioWaveformVisualizer:
    """
    Creates dynamic visual waveforms synchronized to speech audio.
    """

    @classmethod
    def generate_visualizer_spec(
        cls,
        style: WaveformStyle = WaveformStyle.OSCILLOSCOPE_LINE,
        color_hex: str = "#00FFCC",
        width: int = 1280,
        height: int = 240,
        fps: int = 30
    ) -> WaveformVisualizerSpec:
        clean_color = color_hex.replace("#", "0x")

        if style == WaveformStyle.FREQUENCY_BARS:
            f_str = f"showfreqs=s={width}x{height}:mode=bar:ascale=log:fscale=log:colors={clean_color}"
        elif style == WaveformStyle.SPECTROGRAM:
            f_str = f"showspectrum=s={width}x{height}:slide=scroll:color=fire:scale=log"
        elif style == WaveformStyle.CIRCULAR_PULSE:
            f_str = f"showwaves=s={width}x{height}:mode=p2p:rate={fps}:colors={clean_color}"
        else:  # OSCILLOSCOPE_LINE
            f_str = f"showwaves=s={width}x{height}:mode=line:rate={fps}:colors={clean_color}"

        return WaveformVisualizerSpec(
            style=style,
            width=width,
            height=height,
            color_hex=color_hex,
            background_transparent=True,
            ffmpeg_filter=f_str,
            output_fps=fps
        )

