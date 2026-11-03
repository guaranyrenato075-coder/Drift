"""
B-Roll Stock Audio Leveler & Normalizer for CutWire Drift AI.
Equalizes chaotic natural sound volumes across disparate stock video clips
(e.g., loud ocean roar vs quiet library footage), normalizing secondary audio to a gentle -24.0 dB bed.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class NormalizedClipAudioSpec:
    scene_order: int
    raw_source_rms_db: float
    applied_gain_db: float
    target_bed_volume_db: float  # Standard: -24.0 dB
    ffmpeg_volume_filter: str

class BRollAudioLeveler:
    """
    Prevents jarring volume jumps in background B-roll audio.
    """

    TARGET_BED_DB = -24.0  # Background ambient bed standard

    @classmethod
    def calculate_leveling_chain(cls, plan: ProjectPlan) -> List[NormalizedClipAudioSpec]:
        specs: List[NormalizedClipAudioSpec] = []

        for idx, scene in enumerate(getattr(plan, "scenes", [])):
            # Heuristic estimation of ambient intensity based on scene tags
            text_lower = f"{scene.narration_text} {scene.visual_description}".lower()

            if any(w in text_lower for w in ["tempestade", "trânsito", "mar", "ondas", "explosão", "multidão"]):
                raw_rms = -12.0  # Very loud raw sound
            elif any(w in text_lower for w in ["quarto", "livro", "estudo", "silêncio", "noite"]):
                raw_rms = -32.0  # Quiet
            else:
                raw_rms = -18.0  # Moderate

            # Calculate necessary gain to reach target -24dB
            gain_needed = round(cls.TARGET_BED_DB - raw_rms, 1)
            filter_str = f"volume={gain_needed}dB"

            specs.append(
                NormalizedClipAudioSpec(
                    scene_order=scene.order,
                    raw_source_rms_db=raw_rms,
                    applied_gain_db=gain_needed,
                    target_bed_volume_db=cls.TARGET_BED_DB,
                    ffmpeg_volume_filter=filter_str
                )
            )

        return specs

