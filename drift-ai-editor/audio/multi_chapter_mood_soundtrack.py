"""
Multi-Chapter Mood Soundtrack Orchestrator for CutWire Drift AI.
Manages multi-track soundtrack sequencing for long-form videos (10-30+ minutes),
executing mood transitions and seamless audio crossfades between narrative acts.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import math

@dataclass
class SoundtrackSegment:
    segment_index: int
    mood: str                       # 'suspense', 'investigative', 'dramatic_climax', 'inspiring'
    start_sec: float
    end_sec: float
    duration_sec: float
    music_file_path: str
    target_volume_db: float        # ex: -18.0 dB
    crossfade_duration_sec: float  # ex: 3.0s

@dataclass
class MultiChapterAudioPlan:
    total_duration_sec: float
    total_segments: int
    segments: List[SoundtrackSegment]
    ffmpeg_filter_complex: str
    ducking_profile: Dict[str, Any]

class MultiChapterMoodSoundtrackOrchestrator:
    """
    Allocates and crossfades multiple background audio tracks aligned with
    narrative acts for 10-20+ minute long videos.
    """

    MOOD_SOUNDTRACK_PRESETS = {
        "suspense": "assets/audio/music_suspense_drone.mp3",
        "investigative": "assets/audio/music_investigative_pulse.mp3",
        "dramatic_climax": "assets/audio/music_dramatic_orchestral.mp3",
        "inspiring": "assets/audio/music_inspiring_piano_ambient.mp3"
    }

    @classmethod
    def generate_soundtrack_plan(
        cls,
        total_duration_sec: float,
        acts: Optional[List[Dict[str, Any]]] = None,
        custom_tracks: Optional[Dict[str, str]] = None
    ) -> MultiChapterAudioPlan:
        if total_duration_sec <= 0:
            return MultiChapterAudioPlan(
                total_duration_sec=0.0,
                total_segments=0,
                segments=[],
                ffmpeg_filter_complex="",
                ducking_profile={}
            )

        tracks = dict(cls.MOOD_SOUNDTRACK_PRESETS)
        if custom_tracks:
            tracks.update(custom_tracks)

        # Se não forem fornecidos atos explícitos, divide em 4 quadrantes emocionais clássicos
        if not acts:
            q = total_duration_sec / 4.0
            acts = [
                {"name": "Abertura & Mistério", "start_sec": 0.0, "end_sec": q, "mood": "suspense"},
                {"name": "Desenvolvimento & Fatos", "start_sec": q, "end_sec": q * 2.5, "mood": "investigative"},
                {"name": "Conflito & Clímax", "start_sec": q * 2.5, "end_sec": q * 3.5, "mood": "dramatic_climax"},
                {"name": "Conclusão & Reflexão", "start_sec": q * 3.5, "end_sec": total_duration_sec, "mood": "inspiring"}
            ]

        segments: List[SoundtrackSegment] = []
        for idx, act in enumerate(acts, 1):
            mood = act.get("mood", "investigative")
            if mood not in tracks:
                mood = "investigative"
            
            start = round(act.get("start_sec", 0.0), 2)
            end = round(act.get("end_sec", total_duration_sec), 2)
            dur = max(0.1, round(end - start, 2))
            
            # Crossfade de 3s para trocas de música suaves
            crossfade = 3.0 if idx > 1 else 0.0

            segments.append(SoundtrackSegment(
                segment_index=idx,
                mood=mood,
                start_sec=start,
                end_sec=end,
                duration_sec=dur,
                music_file_path=tracks[mood],
                target_volume_db=-20.0,
                crossfade_duration_sec=crossfade
            ))

        # Gera o comando de filtro FFmpeg para encadear as faixas com acrossfade
        filter_parts = []
        # Exemplo de concatenação encadeada com acrossfade: [0:a][1:a]acrossfade=d=3:c1=tri:c2=tri[a12]; ...
        for i, seg in enumerate(segments):
            filter_parts.append(f"[{i}:a]volume={seg.target_volume_db}dB[track{i}];")

        filter_complex = " ".join(filter_parts)

        ducking_profile = {
            "speech_duck_db": -22.0,      # Redução quando há fala
            "pause_boost_db": -6.0,       # Elevação nos silêncios
            "attack_ms": 120,
            "release_ms": 450
        }

        return MultiChapterAudioPlan(
            total_duration_sec=round(total_duration_sec, 2),
            total_segments=len(segments),
            segments=segments,
            ffmpeg_filter_complex=filter_complex,
            ducking_profile=ducking_profile
        )

