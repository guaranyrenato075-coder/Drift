import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from models.scene_plan import ProjectPlan
from director.command_editor import NaturalLanguageCommandEditor, CommandPlan

@dataclass
class VoiceCopilotResult:
    transcribed_speech: str
    command_plan: CommandPlan
    applied_changes: List[str]
    success: bool
    feedback_audio_cue: str   # 'action_completed', 'needs_clarification', 'rejected'

class VoiceCopilotDirector:
    """
    Talk-to-Edit Voice Copilot:
    Enables speaking editing commands directly to the editor (hands-free):
      - "Corta 2 segundos da cena 3"
      - "Deixe a música de fundo mais suave"
      - "Troque o vídeo da cena 1 por galáxias"
    Dispatches parsed intent through NaturalLanguageCommandEditor and returns voice/visual feedback.
    """

    @classmethod
    def execute_voice_command(
        cls,
        spoken_text: str,
        plan: ProjectPlan
    ) -> VoiceCopilotResult:
        clean_text = spoken_text.strip()
        cmd_plan = NaturalLanguageCommandEditor.parse_instruction(clean_text, plan)

        if not cmd_plan.actions:
            return VoiceCopilotResult(
                transcribed_speech=clean_text,
                command_plan=cmd_plan,
                applied_changes=[],
                success=False,
                feedback_audio_cue="needs_clarification"
            )

        applied = NaturalLanguageCommandEditor.apply_plan(cmd_plan, plan)
        return VoiceCopilotResult(
            transcribed_speech=clean_text,
            command_plan=cmd_plan,
            applied_changes=applied,
            success=True,
            feedback_audio_cue="action_completed"
        )

