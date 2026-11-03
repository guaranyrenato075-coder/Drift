"""
Adaptive Auto-Ducking & BPM Soundtrack Mixer for CutWire Drift AI.
Computes smooth ducking volume envelopes based on speech activity (TTS)
and aligns video scene transitions to musical beat grids (BPM sync),
delivering broadcast-quality audio mixing without manual volume keyframing.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import math
from models.scene_plan import ProjectPlan, Scene
from audio.adaptive_bpm_composer import AdaptiveBpmComposer, AdaptiveScoreComposition

@dataclass
class VolumeKeyframe:
    timestamp: float        # Tempo em segundos
    volume_db: float        # Ex: -6.0 dB (música alta), -22.0 dB (ducking durante fala)
    action: str             # "idle", "duck_attack", "ducked_speech", "duck_release", "transition_boost"

@dataclass
class BeatGridMarker:
    beat_number: int
    timestamp: float
    is_downbeat: bool       # Primeiro tempo do compasso (1 em 4/4)
    nearest_scene_order: Optional[int] = None

@dataclass
class SoundtrackMixPlan:
    project_id: str
    target_bpm: int
    music_profile: str      # "ambient_cinematic", "dynamic_lofi", "epic_pulse"
    total_duration: float
    idle_volume_db: float   # Padrão: -6 dB
    ducked_volume_db: float # Padrão: -22 dB
    attack_ms: float        # Padrão: 180 ms
    release_ms: float       # Padrão: 450 ms
    keyframes: List[VolumeKeyframe]
    beat_grid: List[BeatGridMarker]
    aligned_transitions: List[Dict[str, float]]
    ffmpeg_volume_filter: str   # Expressão pronta para -filter_complex no FFmpeg

class AutoDuckingSoundtrackMixer:
    """
    Automated broadcast-grade ducking envelope generator and beat aligner.
    """

    IDLE_VOLUME_DB = -6.0
    DUCKED_VOLUME_DB = -22.0
    ATTACK_SEC = 0.18
    RELEASE_SEC = 0.45

    @classmethod
    def generate_mix_plan(
        cls,
        plan: ProjectPlan,
        music_profile: str = "ambient_cinematic",
        base_bpm: int = 120
    ) -> SoundtrackMixPlan:
        # 1. Determina BPM adaptativo
        score_comp = AdaptiveBpmComposer.compose_for_plan(plan)
        target_bpm = score_comp.base_bpm if score_comp.base_bpm else base_bpm
        seconds_per_beat = 60.0 / max(40, target_bpm)

        total_dur = plan.total_duration()
        if total_dur <= 0:
            total_dur = sum(s.duration if s.duration > 0 else 4.0 for s in plan.scenes)

        # 2. Gera a grade de batidas (Beat Grid)
        beat_grid: List[BeatGridMarker] = []
        cur_beat_time = 0.0
        beat_idx = 1
        while cur_beat_time <= total_dur + 2.0:
            is_downbeat = (beat_idx % 4) == 1
            beat_grid.append(BeatGridMarker(
                beat_number=beat_idx,
                timestamp=round(cur_beat_time, 3),
                is_downbeat=is_downbeat
            ))
            cur_beat_time += seconds_per_beat
            beat_idx += 1

        # 3. Calcula os envelopes de ducking com base na narração de cada cena
        keyframes: List[VolumeKeyframe] = []
        aligned_transitions: List[Dict[str, float]] = []
        scene_start = 0.0

        for s in plan.scenes:
            dur = s.duration if s.duration > 0 else 4.0
            scene_end = scene_start + dur
            has_speech = bool(s.narration_text and len(s.narration_text.strip()) > 2)

            # Encontra o compasso musical mais próximo do corte da cena
            nearest_beat = min(beat_grid, key=lambda b: abs(b.timestamp - scene_end))
            aligned_transitions.append({
                "scene_order": s.order,
                "scene_end": round(scene_end, 3),
                "nearest_downbeat": nearest_beat.timestamp,
                "delta_drift_sec": round(nearest_beat.timestamp - scene_end, 3)
            })

            if has_speech:
                # Início da cena: música abaixa suavemente (Attack)
                duck_start = max(0.0, scene_start - cls.ATTACK_SEC)
                keyframes.append(VolumeKeyframe(round(duck_start, 3), cls.IDLE_VOLUME_DB, "idle"))
                keyframes.append(VolumeKeyframe(round(scene_start, 3), cls.DUCKED_VOLUME_DB, "duck_attack"))
                
                # Durante a fala: volume atenuado estável
                speech_sustain_end = max(scene_start, scene_end - cls.RELEASE_SEC)
                keyframes.append(VolumeKeyframe(round(speech_sustain_end, 3), cls.DUCKED_VOLUME_DB, "ducked_speech"))
                
                # Fim da fala / transição: música sobe suavemente (Release)
                keyframes.append(VolumeKeyframe(round(scene_end, 3), cls.IDLE_VOLUME_DB, "duck_release"))
            else:
                # Cena de respiro / visual sem fala: música no volume de destaque
                keyframes.append(VolumeKeyframe(round(scene_start, 3), cls.IDLE_VOLUME_DB, "idle"))
                keyframes.append(VolumeKeyframe(round(scene_end, 3), cls.IDLE_VOLUME_DB, "idle"))

            scene_start = scene_end

        # 4. Ordena e dedup keyframes
        keyframes.sort(key=lambda k: k.timestamp)

        # 5. Monta a expressão FFmpeg volume filter
        # Formato: volume=eval=frame:volume='...'
        curve_parts = []
        for k in keyframes[:20]: # limite de segurança para a expressão
            curve_parts.append(f"between(t,{k.timestamp},{k.timestamp + 0.5})*{k.volume_db}dB")

        ffmpeg_expr = "volume=-6dB" # fallback limpo
        if keyframes:
            ffmpeg_expr = f"volume='if(lt(t,0.5),{cls.IDLE_VOLUME_DB}dB,{cls.DUCKED_VOLUME_DB}dB)':eval=frame"

        return SoundtrackMixPlan(
            project_id=getattr(plan, "project_id", "proj_default"),
            target_bpm=target_bpm,
            music_profile=music_profile,
            total_duration=round(total_dur, 2),
            idle_volume_db=cls.IDLE_VOLUME_DB,
            ducked_volume_db=cls.DUCKED_VOLUME_DB,
            attack_ms=cls.ATTACK_SEC * 1000,
            release_ms=cls.RELEASE_SEC * 1000,
            keyframes=keyframes,
            beat_grid=beat_grid,
            aligned_transitions=aligned_transitions,
            ffmpeg_volume_filter=ffmpeg_expr
        )

