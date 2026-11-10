"""
Multi-Track Audio Stem Splitter & Mixer for CutWire Drift AI.
Manages isolated audio stems (Dialogue/Voice, Musical Soundtrack, and Foley/SFX)
with independent faders, panning, and master export capabilities for DAW interoperability
(DaVinci Resolve, Premiere Pro, Audacity, and native Drift timeline).
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
from models.scene_plan import ProjectPlan

@dataclass
class AudioStemTrack:
    stem_id: str
    name: str
    channel_type: str  # "dialogue", "music", "sfx"
    gain_db: float
    is_muted: bool
    is_solo: bool
    file_path: Optional[str] = None

@dataclass
class StemMixerManifest:
    project_id: str
    sample_rate_hz: int
    bit_depth: int
    master_gain_db: float
    tracks: List[AudioStemTrack]
    export_ready: bool

class AudioStemSplitter:
    """
    Orchestrates discrete audio stems and multi-bus timeline mixing.
    """

    @classmethod
    def create_default_mixer_manifest(cls, plan: ProjectPlan) -> StemMixerManifest:
        tracks = [
            AudioStemTrack(
                stem_id="stem_dialogue",
                name="Voz & Narração Principal (Dialogue)",
                channel_type="dialogue",
                gain_db=0.0,
                is_muted=False,
                is_solo=False
            ),
            AudioStemTrack(
                stem_id="stem_music",
                name="Trilha Sonora Ambiente (Soundtrack)",
                channel_type="music",
                gain_db=-14.0,  # Pre-ducked
                is_muted=False,
                is_solo=False
            ),
            AudioStemTrack(
                stem_id="stem_sfx",
                name="Efeitos Sonoros & Foley (SFX)",
                channel_type="sfx",
                gain_db=-16.0,
                is_muted=False,
                is_solo=False
            )
        ]

        return StemMixerManifest(
            project_id=plan.project_id,
            sample_rate_hz=48000,
            bit_depth=24,
            master_gain_db=0.0,
            tracks=tracks,
            export_ready=any(s.audio_path for s in plan.scenes)
        )

    @classmethod
    def generate_ffmpeg_stem_filter(cls, manifest: StemMixerManifest) -> str:
        """
        Builds the FFmpeg complex audio filter graph to blend stems with volume faders.
        """
        active_inputs = []
        filter_lines = []
        idx = 0
        for t in manifest.tracks:
            if not t.is_muted:
                vol_linear = 10.0 ** (t.gain_db / 20.0)
                filter_lines.append(f"[{idx}:a]volume={vol_linear:.4f}[a{idx}]")
                active_inputs.append(f"[a{idx}]")
                idx += 1

        if not active_inputs:
            return "anull"

        in_str = "".join(active_inputs)
        filter_lines.append(f"{in_str}amix=inputs={len(active_inputs)}:duration=longest:dropout_transition=0.5[outa]")
        return ";".join(filter_lines)
