"""
Character Continuity Director for CutWire Drift AI.
Tracks recurring characters across scenes, anchors visual traits (hair, wardrobe, ethnicity, age, style),
and audits scene prompt descriptors to ensure visual consistency.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class CharacterPersona:
    character_id: str
    name: str
    gender: str
    age_range: str
    visual_signature: str  # e.g., "Cyberpunk hacker, bright neon blue undercut, dark trenchcoat with glowing cyan collar"
    fixed_traits: List[str] = field(default_factory=list)
    seed_override: Optional[int] = None

@dataclass
class ContinuityAuditResult:
    scene_index: int
    character_id: str
    is_consistent: bool
    missing_traits: List[str]
    suggested_prompt_prefix: str

class CharacterContinuityTracker:
    """
    Maintains character bible and validates scene prompts against registered personas.
    """

    def __init__(self):
        self.personas: Dict[str, CharacterPersona] = {}

    def register_persona(self, persona: CharacterPersona):
        self.personas[persona.character_id] = persona

    def generate_prompt_anchor(self, character_id: str) -> str:
        """
        Creates an immutable prompt prefix ensuring AI image engines preserve the persona.
        """
        if character_id not in self.personas:
            return ""
        p = self.personas[character_id]
        traits_str = ", ".join(p.fixed_traits)
        return f"{p.name}, {p.age_range}, {p.visual_signature}, {traits_str}".strip(", ")

    def audit_scene(self, scene_index: int, character_id: str, scene_description: str) -> ContinuityAuditResult:
        """
        Checks if a scene prompt contains the registered character's mandatory traits.
        """
        if character_id not in self.personas:
            return ContinuityAuditResult(
                scene_index=scene_index,
                character_id=character_id,
                is_consistent=True,
                missing_traits=[],
                suggested_prompt_prefix=""
            )

        persona = self.personas[character_id]
        desc_lower = scene_description.lower()
        missing = [t for t in persona.fixed_traits if t.lower() not in desc_lower]

        anchor = self.generate_prompt_anchor(character_id)
        is_consistent = len(missing) == 0

        return ContinuityAuditResult(
            scene_index=scene_index,
            character_id=character_id,
            is_consistent=is_consistent,
            missing_traits=missing,
            suggested_prompt_prefix=anchor
        )

