"""
Cinematic Credits Roll Generator for CutWire Drift AI.
Generates moving vertical end credits sequences featuring production roles,
soundtrack titles, and automated attribution manifests compiled from the 26 media providers.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class CreditSection:
    heading: str
    names_or_lines: List[str]

@dataclass
class CreditsRollPlan:
    duration_sec: float
    total_sections: int
    raw_credits_text: str
    ffmpeg_drawtext_filter: str

class CreditsRollGenerator:
    """
    Synthesizes elegant Hollywood-style end credits rolls.
    """

    @classmethod
    def generate_credits(
        cls,
        plan: ProjectPlan,
        director_name: str = "CutWire Drift AI Director",
        music_credit: str = "Trilhas Sonoras Royalty-Free CC",
        duration_sec: float = 8.0
    ) -> CreditsRollPlan:
        sections = [
            CreditSection("DIREÇÃO E MONTAGEM", [director_name]),
            CreditSection("ROTEIRO E PESQUISA", [plan.title or "Produção Audiovisual"]),
            CreditSection("MÚSICA E AMBIÊNCIAS", [music_credit])
        ]

        # Extract attribution creators from plan
        used_creators = set()
        for s in getattr(plan, "scenes", []):
            med = getattr(s, "selected_media", None)
            if med and med.creator:
                used_creators.add(f"{med.creator} ({med.platform.capitalize()})")

        if used_creators:
            sections.append(CreditSection("ACERVO E BANCOS DE MÍDIA", sorted(list(used_creators))[:8]))

        # Format scroll text
        lines = ["", "", "*** CRÉDITOS FINAIS ***", ""]
        for sec in sections:
            lines.append(f"--- {sec.heading} ---")
            for item in sec.names_or_lines:
                lines.append(item)
            lines.append("")

        full_text = "\n".join(lines)

        # Build FFmpeg drawtext scroll filter: y=h-(t/duration)*(h+text_h)
        filter_str = (
            f"drawtext=text='{director_name}':fontsize=32:fontcolor=white:"
            f"x=(w-text_w)/2:y=h-(t/{duration_sec})*(h+400)"
        )

        return CreditsRollPlan(
            duration_sec=duration_sec,
            total_sections=len(sections),
            raw_credits_text=full_text,
            ffmpeg_drawtext_filter=filter_str
        )

