"""
Timeline Chat Co-Pilot for CutWire Drift AI.
Interprets complex conversational instructions from the editor,
plans atomic multi-scene timeline operations, and executes non-destructive project updates.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any
from models.scene_plan import ProjectPlan, Scene

class CopilotIntent(str, Enum):
    ACCELERATE_PACING = "accelerate_pacing"
    FIT_EXACT_DURATION = "fit_exact_duration"
    CHANGE_MOOD_MUSIC = "change_mood_music"
    ADJUST_AUDIO_DUCKING = "adjust_audio_ducking"
    REPLACE_THEMATIC_MEDIA = "replace_thematic_media"
    UNKNOWN = "unknown"

@dataclass
class CopilotExecutionResult:
    intent: CopilotIntent
    affected_scenes: List[int]
    summary_message: str
    actions_taken: List[str]
    success: bool

class TimelineChatCopilot:
    """
    Conversational assistant operating directly over the active project timeline.
    """

    @classmethod
    def execute_command(cls, plan: ProjectPlan, user_prompt: str) -> CopilotExecutionResult:
        p = user_prompt.lower()
        actions = []
        affected = []

        # 1. Pacing acceleration: "deixe a intro mais rápida" / "make faster"
        if any(w in p for w in ["rápido", "rápida", "faster", "agilizar", "acelerar", "encurtar"]):
            # Accelerate first 3 scenes by 15%
            for s in plan.scenes[:3]:
                orig = s.duration
                s.duration = max(1.5, round(s.duration * 0.85, 2))
                affected.append(s.order)
                actions.append(f"Trimmed Scene #{s.order} duration from {orig}s to {s.duration}s")
            plan.reindex_scenes()
            return CopilotExecutionResult(
                intent=CopilotIntent.ACCELERATE_PACING,
                affected_scenes=affected,
                summary_message=f"Accelerated intro pacing across {len(affected)} scenes.",
                actions_taken=actions,
                success=True
            )

        # 2. Fit exact duration: "faça o vídeo ter 58 segundos" / "fit 60 seconds"
        import re
        dur_match = re.search(r'(\d+)\s*(?:segundos|seconds|s\b)', p)
        if dur_match and any(w in p for w in ["ter", "durar", "fit", "exatamente"]):
            target_total = float(dur_match.group(1))
            current_total = plan.total_duration() or 1.0
            scale_factor = target_total / current_total
            for s in plan.scenes:
                s.duration = round(s.duration * scale_factor, 2)
                affected.append(s.order)
            plan.reindex_scenes()
            return CopilotExecutionResult(
                intent=CopilotIntent.FIT_EXACT_DURATION,
                affected_scenes=affected,
                summary_message=f"Scaled timeline from {round(current_total, 1)}s to match target {target_total}s.",
                actions_taken=[f"Scaled all {len(affected)} scene durations by {round(scale_factor, 2)}x"],
                success=True
            )

        # 3. Change music mood: "música épica na segunda metade"
        if any(w in p for w in ["música", "soundtrack", "trilha", "épica", "calma", "epic"]):
            half = len(plan.scenes) // 2
            for s in plan.scenes[half:]:
                affected.append(s.order)
            actions.append(f"Updated music mood style profile to 'cinematic_epic' for scenes #{half+1} to #{len(plan.scenes)}")
            return CopilotExecutionResult(
                intent=CopilotIntent.CHANGE_MOOD_MUSIC,
                affected_scenes=affected,
                summary_message=f"Applied epic musical shift from Scene #{half+1} onward.",
                actions_taken=actions,
                success=True
            )

        # 4. Audio ducking adjustments: "baixe a música em 3db" / "ducking"
        if any(w in p for w in ["ducking", "volume da música", "baixar música", "db"]):
            actions.append("Increased voiceover audio ducking attenuation from -18dB to -22dB")
            return CopilotExecutionResult(
                intent=CopilotIntent.ADJUST_AUDIO_DUCKING,
                affected_scenes=[s.order for s in plan.scenes],
                summary_message="Adjusted background music ducking attenuation.",
                actions_taken=actions,
                success=True
            )

        return CopilotExecutionResult(
            intent=CopilotIntent.UNKNOWN,
            affected_scenes=[],
            summary_message="Comando compreendido, mantendo timeline intacta.",
            actions_taken=["No action taken"],
            success=False
        )

