"""
Kinetic Infographics & Data Visualization Engine for CutWire Drift AI.
Detects statistics, percentages, numerical metrics, and dates in narrative text,
and generates kinetic counter animations, progress bars, and infographic lower-thirds.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import re

class InfographicType(str, Enum):
    PERCENTAGE_COUNTER = "percentage_counter"
    CURRENCY_GROWTH = "currency_growth"
    BAR_COMPARISON = "bar_comparison"
    YEAR_TIMELINE_STAMP = "year_timeline_stamp"

@dataclass
class KineticInfographicOverlay:
    scene_index: int
    infographic_type: InfographicType
    headline: str
    target_value: float
    unit_prefix: str
    unit_suffix: str
    start_time: float
    duration: float
    render_spec: Dict[str, str]

class KineticInfographicsEngine:
    """
    Parses quantitative statements into synchronized motion graphics specifications.
    """

    PERCENT_PATTERN = re.compile(r'(\d+(?:[.,]\d+)?)\s*%', re.IGNORECASE)
    CURRENCY_PATTERN = re.compile(r'(?:R\$|\$|US\$|€)\s*(\d+(?:[.,]\d+)?)', re.IGNORECASE)
    YEAR_PATTERN = re.compile(r'\b(1[89]\d\d|20\d\d)\b')

    @classmethod
    def scan_scene_data(cls, scene_index: int, narration_text: str, start_time: float, duration: float) -> Optional[KineticInfographicOverlay]:
        # 1. Percentages (e.g. 42%)
        p_match = cls.PERCENT_PATTERN.search(narration_text)
        if p_match:
            val = float(p_match.group(1).replace(",", "."))
            return KineticInfographicOverlay(
                scene_index=scene_index,
                infographic_type=InfographicType.PERCENTAGE_COUNTER,
                headline="Índice de Crescimento",
                target_value=val,
                unit_prefix="",
                unit_suffix="%",
                start_time=round(start_time, 2),
                duration=round(duration, 2),
                render_spec={
                    "animation": "ease_out_counter",
                    "color_accent": "#00FFCC",
                    "font_weight": "bold"
                }
            )

        # 2. Currency values
        c_match = cls.CURRENCY_PATTERN.search(narration_text)
        if c_match:
            val = float(c_match.group(1).replace(",", "."))
            return KineticInfographicOverlay(
                scene_index=scene_index,
                infographic_type=InfographicType.CURRENCY_GROWTH,
                headline="Volume Financeiro",
                target_value=val,
                unit_prefix="$",
                unit_suffix="",
                start_time=round(start_time, 2),
                duration=round(duration, 2),
                render_spec={
                    "animation": "odometer_roll",
                    "color_accent": "#2ECC71",
                    "font_weight": "bold"
                }
            )

        # 3. Historical years
        y_match = cls.YEAR_PATTERN.search(narration_text)
        if y_match:
            val = float(y_match.group(1))
            return KineticInfographicOverlay(
                scene_index=scene_index,
                infographic_type=InfographicType.YEAR_TIMELINE_STAMP,
                headline="Marco Histórico",
                target_value=val,
                unit_prefix="Ano ",
                unit_suffix="",
                start_time=round(start_time, 2),
                duration=round(duration, 2),
                render_spec={
                    "animation": "fade_slide_up",
                    "color_accent": "#F1C40F",
                    "font_weight": "800"
                }
            )

        return None

