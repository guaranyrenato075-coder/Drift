"""
Transition Monotony Detector & Dynamic Variety Engine for CutWire Drift AI.
Audits consecutive cut transitions across the timeline, flags repetitive cut streaks (>3 identical cuts),
and prescribes diverse transition techniques (J-Cut, L-Cut, Whip Pan, Cross-Dissolve, Match Cut).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

class TransitionKind(str, Enum):
    HARD_CUT = "hard_cut"
    J_CUT = "j_cut"                     # Audio leads video by 0.5s
    L_CUT = "l_cut"                     # Video leads audio by 0.5s
    CROSS_DISSOLVE = "cross_dissolve"
    WHIP_PAN = "whip_pan"
    MATCH_CUT = "match_cut"

@dataclass
class TransitionMonotonyAlert:
    start_scene_order: int
    streak_count: int
    overused_transition: str
    suggested_variety_sequence: List[str]

@dataclass
class TransitionVarietyReport:
    total_transitions: int
    is_diverse: bool
    transition_distribution: Dict[str, int]
    alerts: List[TransitionMonotonyAlert]

class TransitionMonotonyDetector:
    """
    Prevents editorial monotony by regulating transition rhythms.
    """

    MAX_CONSECUTIVE_IDENTICAL_CUTS = 3

    @classmethod
    def audit_transitions(cls, plan: ProjectPlan) -> TransitionVarietyReport:
        if not plan.scenes or len(plan.scenes) < 2:
            return TransitionVarietyReport(0, True, {}, [])

        transitions = []
        for s in plan.scenes:
            t = getattr(s, "transition", "hard_cut") or "hard_cut"
            transitions.append(t)

        dist: Dict[str, int] = {}
        alerts: List[TransitionMonotonyAlert] = []

        streak = 1
        current_type = transitions[0]

        for i in range(1, len(transitions)):
            t = transitions[i]
            dist[t] = dist.get(t, 0) + 1

            if t == current_type:
                streak += 1
                if streak > cls.MAX_CONSECUTIVE_IDENTICAL_CUTS:
                    alerts.append(
                        TransitionMonotonyAlert(
                            start_scene_order=plan.scenes[i - streak + 1].order,
                            streak_count=streak,
                            overused_transition=current_type,
                            suggested_variety_sequence=["j_cut", "cross_dissolve", "whip_pan"]
                        )
                    )
            else:
                streak = 1
                current_type = t

        return TransitionVarietyReport(
            total_transitions=len(transitions) - 1,
            is_diverse=(len(alerts) == 0),
            transition_distribution=dist,
            alerts=alerts
        )

