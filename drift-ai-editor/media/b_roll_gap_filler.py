"""
B-Roll Gap Filler for CutWire Drift AI.
Detects abstract concepts, historical entities, and visual pauses in scripts,
sourcing and allocating cinematic overlay B-Roll from curated open museum/science archives
(NASA, Smithsonian, Met Museum, Library of Congress, Wikimedia).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re

@dataclass
class BRollInsertion:
    target_scene_order: int
    matched_concept: str
    overlay_type: str             # 'picture_in_picture', 'full_cutaway', 'lower_third_asset'
    recommended_provider: str     # 'nasa', 'smithsonian', 'met_museum', 'wikimedia', 'loc'
    search_query_pt: str
    search_query_en: str
    start_offset_sec: float
    duration_sec: float
    blend_opacity: float          # 0.0 to 1.0

@dataclass
class BRollPlan:
    total_insertions: int
    insertions: List[BRollInsertion]
    coverage_ratio: float

class BRollGapFiller:
    """
    Identifies visual coverage opportunities and schedules B-Roll archival footage.
    """

    ARCHIVE_CONCEPT_MAP = {
        "espaço": ("nasa", "espaço sideral astronomia", "outer space astronomy galaxy"),
        "galáxia": ("nasa", "galáxia nebulosa telescópio", "galaxy nebula telescope"),
        "lua": ("nasa", "lua apollo exploração lunar", "moon apollo lunar surface"),
        "história": ("smithsonian", "artefatos históricos arquivo", "historical artifacts archives"),
        "roma": ("met_museum", "império romano estátua antiga", "ancient roman empire sculpture"),
        "grego": ("met_museum", "grécia antiga arte clássica", "ancient greece classical art"),
        "guerra": ("loc", "arquivos históricos documento", "historical war archives vintage"),
        "natureza": ("biodiversity", "vida selvagem biodiversidade", "wildlife biodiversity flora"),
        "física": ("wikimedia", "experimento laboratório ciência", "physics science experiment lab"),
        "evolução": ("smithsonian", "fóssil esqueleto evolução", "fossil evolution skeleton")
    }

    @classmethod
    def identify_broll_opportunities(
        cls,
        scene_order: int,
        narration: str,
        scene_duration: float = 6.0
    ) -> List[BRollInsertion]:
        insertions: List[BRollInsertion] = []
        narration_lower = narration.lower()

        # Só insere B-Roll se a cena tiver mais de 4 segundos
        if scene_duration < 4.0:
            return []

        for key, (prov, q_pt, q_en) in cls.ARCHIVE_CONCEPT_MAP.items():
            if key in narration_lower:
                # Aloca o B-roll no meio da cena (ex: dos 2s aos 5s)
                dur = min(3.5, scene_duration * 0.6)
                offset = max(1.0, (scene_duration - dur) / 2.0)
                
                insertions.append(BRollInsertion(
                    target_scene_order=scene_order,
                    matched_concept=key,
                    overlay_type="full_cutaway" if scene_duration > 7.0 else "picture_in_picture",
                    recommended_provider=prov,
                    search_query_pt=q_pt,
                    search_query_en=q_en,
                    start_offset_sec=round(offset, 1),
                    duration_sec=round(dur, 1),
                    blend_opacity=1.0 if scene_duration > 7.0 else 0.90
                ))
                break # 1 B-Roll principal por cena

        return insertions

    @classmethod
    def generate_plan(cls, scenes: List[Any]) -> BRollPlan:
        all_insertions: List[BRollInsertion] = []

        for sc in scenes:
            text = getattr(sc, "narration_text", "") or getattr(sc, "text", "")
            order = getattr(sc, "order", 1)
            dur = getattr(sc, "duration", 6.0) or 6.0

            found = cls.identify_broll_opportunities(order, text, dur)
            all_insertions.extend(found)

        total_scenes = max(1, len(scenes))
        coverage = round(len(all_insertions) / total_scenes, 2)

        return BRollPlan(
            total_insertions=len(all_insertions),
            insertions=all_insertions,
            coverage_ratio=coverage
        )

