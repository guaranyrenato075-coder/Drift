import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene
from pipeline.job_manager import JobManager, JobStage, PipelineJob
from pipeline.timeline_planner import TimelinePlanner, AssemblyPlan
from pipeline.quality_control import QualityControlEngine, QualityAuditReport
from analysis.storyboard_engine import StoryboardEngine
from media.media_ranker import MediaRanker
from director.command_editor import NaturalLanguageCommandEditor, CommandPlan

logger = logging.getLogger("drift.director.orchestrator")

@dataclass
class AgentResult:
    agent_name: str
    success: bool
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class AiDirectorOrchestrator:
    """
    Central AI Director Agent:
    Acts as the master conductor orchestrating specialized task agents:
      - ScriptAgent: Roteiro, ganchos e intenções semânticas.
      - VoiceAgent: Alinhamento de áudio real e síntese fonética.
      - VisualSearchAgent: Busca, ranqueamento e galerias de alternativas.
      - AssemblyAgent: Plano prévio e execução em lotes protegidos.
      - QualityAgent: Auditoria, safe-zones e conformidade de direitos autorais.
      - CommandAgent: Edição por comandos em linguagem natural.
    """

    def __init__(self, job_manager: Optional[JobManager] = None):
        self.job_manager = job_manager or JobManager()

    def process_command(self, plan: ProjectPlan, user_command: str) -> AgentResult:
        """Processes conversational instruction, applies planned changes, and audits impact."""
        logger.info(f"Diretor de IA recebeu comando: '{user_command}'")
        cmd_plan = NaturalLanguageCommandEditor.parse_instruction(user_command, plan)
        if not cmd_plan.actions:
            return AgentResult(
                agent_name="CommandAgent",
                success=False,
                summary=cmd_plan.summary_message,
                errors=["Comando não reconhecido."]
            )

        applied_msgs = NaturalLanguageCommandEditor.apply_plan(cmd_plan, plan)
        audit = QualityControlEngine.audit_project(plan)

        return AgentResult(
            agent_name="CommandAgent",
            success=True,
            summary="; ".join(applied_msgs),
            data={
                "command_plan": cmd_plan.__dict__,
                "audit_score": audit.score,
                "project_id": plan.project_id
            }
        )

    def plan_full_production(
        self,
        plan: ProjectPlan,
        style_id: str = "filosofico"
    ) -> AssemblyPlan:
        """
        Coordinates full pre-flight production plan across all specialist agents
        before any modification touches Drift's timeline.
        """
        # 1. Script & Storyboard Agent
        intents = StoryboardEngine.apply_storyboard(plan.scenes)

        # 2. Timeline Planning Agent
        from pipeline.style_engine import StyleEngine
        profile = StyleEngine.get_profile(style_id)
        assembly_plan = TimelinePlanner.create_assembly_plan(plan, profile)

        return assembly_plan

