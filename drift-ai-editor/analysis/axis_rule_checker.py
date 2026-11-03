"""
180-Degree Axis Rule & Eyeline Continuity Checker for CutWire Drift AI.
Audits consecutive narrative cuts for spatial continuity, vector direction
(left-to-right vs right-to-left), and warns against jarring 180-degree line jumps.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

class ScreenDirection(str, Enum):
    LOOKING_RIGHT = "looking_right"    # Subject on left looking right
    LOOKING_LEFT = "looking_left"      # Subject on right looking left
    CENTER_FACING = "center_facing"    # Neutral/Frontal
    MOVING_EAST = "moving_east"        # Left-to-right movement
    MOVING_WEST = "moving_west"        # Right-to-left movement

@dataclass
class AxisViolationAlert:
    from_scene_order: int
    to_scene_order: int
    prior_direction: ScreenDirection
    subsequent_direction: ScreenDirection
    severity: str  # "warning", "critical"
    recommendation: str

@dataclass
class AxisContinuityReport:
    total_cuts_audited: int
    violations_detected: int
    alerts: List[AxisViolationAlert] = field(default_factory=list)
    is_continuity_preserved: bool = True

class AxisRuleChecker:
    """
    Enforces classical film grammar and prevents jarring eyeline / vector reversals.
    """

    @classmethod
    def audit_timeline(cls, plan: ProjectPlan) -> AxisContinuityReport:
        if not plan.scenes or len(plan.scenes) < 2:
            return AxisContinuityReport(0, 0, [], True)

        alerts: List[AxisViolationAlert] = []
        prior_dir = ScreenDirection.CENTER_FACING

        for i in range(1, len(plan.scenes)):
            s_prev = plan.scenes[i - 1]
            s_curr = plan.scenes[i]

            dir_prev = cls._infer_direction(s_prev.visual_description)
            dir_curr = cls._infer_direction(s_curr.visual_description)

            # Detect illegal jump: dialogue cut where both speakers look in the identical direction
            if dir_prev == ScreenDirection.LOOKING_RIGHT and dir_curr == ScreenDirection.LOOKING_RIGHT:
                alerts.append(
                    AxisViolationAlert(
                        from_scene_order=s_prev.order,
                        to_scene_order=s_curr.order,
                        prior_direction=dir_prev,
                        subsequent_direction=dir_curr,
                        severity="warning",
                        recommendation="Both consecutive subjects look Right. Flip/Mirror clipe or pick an alternative shot looking Left."
                    )
                )
            elif dir_prev == ScreenDirection.MOVING_EAST and dir_curr == ScreenDirection.MOVING_WEST:
                alerts.append(
                    AxisViolationAlert(
                        from_scene_order=s_prev.order,
                        to_scene_order=s_curr.order,
                        prior_direction=dir_prev,
                        subsequent_direction=dir_curr,
                        severity="critical",
                        recommendation="Screen movement vector abruptly flipped from East to West across cuts."
                    )
                )

        return AxisContinuityReport(
            total_cuts_audited=len(plan.scenes) - 1,
            violations_detected=len(alerts),
            alerts=alerts,
            is_continuity_preserved=(len(alerts) == 0)
        )

    @classmethod
    def _infer_direction(cls, visual_desc: str) -> ScreenDirection:
        t = visual_desc.lower()
        if any(w in t for w in ["olhando para a direita", "looking right", "olhar à direita"]):
            return ScreenDirection.LOOKING_RIGHT
        elif any(w in t for w in ["olhando para a esquerda", "looking left", "olhar à esquerda"]):
            return ScreenDirection.LOOKING_LEFT
        elif any(w in t for w in ["correndo para a direita", "moving east", "da esquerda para a direita"]):
            return ScreenDirection.MOVING_EAST
        elif any(w in t for w in ["correndo para a esquerda", "moving west", "da direita para a esquerda"]):
            return ScreenDirection.MOVING_WEST
        return ScreenDirection.CENTER_FACING

