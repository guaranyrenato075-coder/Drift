"""
Motion Infographics & Counter FX Generator for CutWire Drift AI (Vox / Johnny Harris Style).
Detects statistical data, percentages, historical years, and financial figures in the script,
generating animated on-screen counters, progress bars, and infographic visual overlays.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re

@dataclass
class InfographicItem:
    scene_order: int
    data_type: str            # 'percentage', 'historical_year', 'financial', 'large_number'
    raw_match: str
    target_value: float
    unit_prefix: str
    unit_suffix: str
    label_text: str
    start_time_sec: float
    duration_sec: float
    ffmpeg_drawtext_filter: str

@dataclass
class InfographicsPlan:
    total_elements: int
    items: List[InfographicItem]
    style_theme: str          # 'vox_dark_minimalist', 'kurzgesagt_vibrant', 'financial_terminal'

class MotionInfographicsGenerator:
    """
    Parses script narrations to uncover key numeric milestones and renders dynamic visual counters.
    """

    PATTERNS = {
        "percentage": re.compile(r'(\d+(?:[.,]\d+)?)\s*%', re.IGNORECASE),
        "historical_year": re.compile(r'\b(?:em|no ano de|desde)\s*(1[789]\d\d|20\d\d)\b', re.IGNORECASE),
        "financial": re.compile(r'(?:R\$|\$|US\$|€)\s*(\d+(?:[.,]\d+)?(?:\s*(?:milhões|bilhões|mil|k|m|b))?)', re.IGNORECASE),
        "large_number": re.compile(r'(\d+(?:[.,]\d+)?)\s*(milhões|bilhões|trilhões|mil)\b', re.IGNORECASE)
    }

    @classmethod
    def scan_scene_for_infographics(
        cls,
        scene_order: int,
        narration: str,
        start_time_sec: float = 0.0,
        duration_sec: float = 5.0,
        style: str = "vox_dark_minimalist"
    ) -> List[InfographicItem]:
        items: List[InfographicItem] = []

        # 1. Porcentagem (ex: "74%")
        pct_match = cls.PATTERNS["percentage"].search(narration)
        if pct_match:
            raw_val = float(pct_match.group(1).replace(",", "."))
            filter_str = (
                f"drawtext=text='%{{eif\\:trunc(min({raw_val}\\,{raw_val}*t/{max(0.5, duration_sec * 0.7)}))\\:d}}%':"
                f"x=(w-text_w)/2:y=(h-text_h)/2:fontsize=84:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=24"
            )
            items.append(InfographicItem(
                scene_order=scene_order,
                data_type="percentage",
                raw_match=pct_match.group(0),
                target_value=raw_val,
                unit_prefix="",
                unit_suffix="%",
                label_text=f"Índice: {pct_match.group(0)}",
                start_time_sec=start_time_sec,
                duration_sec=duration_sec,
                ffmpeg_drawtext_filter=filter_str
            ))

        # 2. Anos históricos (ex: "Em 1969")
        year_match = cls.PATTERNS["historical_year"].search(narration)
        if year_match:
            year_val = float(year_match.group(1))
            filter_str = (
                f"drawtext=text='ANO %{{eif\\:trunc(min({year_val}\\,{year_val-20}+20*t/{max(0.5, duration_sec * 0.6)}))\\:d}}':"
                f"x=(w-text_w)/2:y=(h-text_h)/2-40:fontsize=76:fontcolor=0xfbbf24:box=1:boxcolor=0x18181b@0.75:boxborderw=20"
            )
            items.append(InfographicItem(
                scene_order=scene_order,
                data_type="historical_year",
                raw_match=year_match.group(0),
                target_value=year_val,
                unit_prefix="ANO ",
                unit_suffix="",
                label_text=f"Marco Temporal: {year_match.group(1)}",
                start_time_sec=start_time_sec,
                duration_sec=duration_sec,
                ffmpeg_drawtext_filter=filter_str
            ))

        # 3. Números de escala (ex: "500 milhões")
        scale_match = cls.PATTERNS["large_number"].search(narration)
        if scale_match and not any(it.raw_match == scale_match.group(0) for it in items):
            base_n = float(scale_match.group(1).replace(",", "."))
            unit = scale_match.group(2).upper()
            filter_str = (
                f"drawtext=text='%{{eif\\:trunc(min({base_n}\\,{base_n}*t/{max(0.5, duration_sec * 0.7)}))\\:d}} {unit}':"
                f"x=(w-text_w)/2:y=(h-text_h)/2:fontsize=80:fontcolor=0x38bdf8:box=1:boxcolor=0x0f172a@0.7:boxborderw=20"
            )
            items.append(InfographicItem(
                scene_order=scene_order,
                data_type="large_number",
                raw_match=scale_match.group(0),
                target_value=base_n,
                unit_prefix="",
                unit_suffix=f" {unit}",
                label_text=scale_match.group(0).title(),
                start_time_sec=start_time_sec,
                duration_sec=duration_sec,
                ffmpeg_drawtext_filter=filter_str
            ))

        return items

    @classmethod
    def scan_project_scenes(
        cls,
        scenes: List[Any],
        style: str = "vox_dark_minimalist"
    ) -> InfographicsPlan:
        all_items: List[InfographicItem] = []
        cur_time = 0.0

        for sc in scenes:
            text = getattr(sc, "narration_text", "") or getattr(sc, "text", "")
            order = getattr(sc, "order", 1)
            dur = getattr(sc, "duration", 5.0) or 5.0

            found = cls.scan_scene_for_infographics(
                scene_order=order,
                narration=text,
                start_time_sec=round(cur_time, 2),
                duration_sec=dur,
                style=style
            )
            all_items.extend(found)
            cur_time += dur

        return InfographicsPlan(
            total_elements=len(all_items),
            items=all_items,
            style_theme=style
        )
