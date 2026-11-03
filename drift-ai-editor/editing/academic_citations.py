"""
Academic & Documentary Citation Director for CutWire Drift AI.
Detects factual claims, links bibliographic references to specific scene timestamps,
generates verified lower-third citation overlays, and formats APA/ABNT credit rolls.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class CitationReference:
    ref_id: str
    authors: str
    year: int
    title: str
    source_venue: str  # e.g., "Nature", "Science Direct", "IBGE 2024"
    doi_or_url: Optional[str] = None

@dataclass
class SceneCitationOverlay:
    scene_index: int
    timestamp_start: float
    timestamp_end: float
    reference: CitationReference
    formatted_lower_third: str

class CitationDirector:
    """
    Manages scientific and documentary source attribution on the video timeline.
    """

    def __init__(self):
        self.bibliography: Dict[str, CitationReference] = {}

    def add_reference(self, ref: CitationReference):
        self.bibliography[ref.ref_id] = ref

    def schedule_overlay(
        self,
        scene_index: int,
        timestamp_start: float,
        duration: float,
        ref_id: str
    ) -> Optional[SceneCitationOverlay]:
        if ref_id not in self.bibliography:
            return None

        ref = self.bibliography[ref_id]
        lower_third = f"Fonte: {ref.authors} ({ref.year}). {ref.title} — {ref.source_venue}"

        return SceneCitationOverlay(
            scene_index=scene_index,
            timestamp_start=round(timestamp_start, 2),
            timestamp_end=round(timestamp_start + duration, 2),
            reference=ref,
            formatted_lower_third=lower_third
        )

    def export_apa_bibliography(self) -> List[str]:
        """Exports ordered list of references in APA format for video description or credits."""
        entries = []
        for ref in sorted(self.bibliography.values(), key=lambda r: (r.authors, r.year)):
            entry = f"{ref.authors} ({ref.year}). {ref.title}. {ref.source_venue}."
            if ref.doi_or_url:
                entry += f" {ref.doi_or_url}"
            entries.append(entry)
        return entries

