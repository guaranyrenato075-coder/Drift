"""
Thumbnail Visual Attention Heatmap Simulator for CutWire Drift AI.
Simulates human foveal eye-tracking in the initial 500ms of mobile YouTube feed browsing,
scoring rule-of-thirds focal balance, text readability contrast, and face prominence.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class HeatmapGridCell:
    row: int  # 0 to 2
    col: int  # 0 to 2
    attention_weight_pct: float  # e.g. 28.5%
    focal_element: str  # "face", "headline_text", "high_contrast", "background"

@dataclass
class ThumbnailHeatmapReport:
    overall_ctr_score: int  # 0 to 100
    primary_focal_point: str
    grid_matrix: List[HeatmapGridCell]
    recommendations: List[str]

class ThumbnailAttentionHeatmap:
    """
    Evaluates visual competition and gaze draw on candidate thumbnail compositions.
    """

    @classmethod
    def analyze_thumbnail(
        cls,
        has_human_face: bool = True,
        text_word_count: int = 4,
        has_high_contrast: bool = True,
        subject_position: str = "right"  # "left", "center", "right"
    ) -> ThumbnailHeatmapReport:
        grid: List[HeatmapGridCell] = []
        ctr_score = 65

        # Base 3x3 grid weights
        weights = [
            [8.0, 12.0, 10.0],
            [14.0, 24.0, 16.0],
            [4.0, 8.0, 4.0]
        ]

        if has_human_face:
            ctr_score += 15
            # Shift focal weight towards face position
            col = 2 if subject_position == "right" else (0 if subject_position == "left" else 1)
            weights[1][col] += 12.0

        if has_high_contrast:
            ctr_score += 10
            weights[0][1] += 5.0

        if text_word_count > 6:
            ctr_score -= 12  # Too text-heavy for mobile

        # Normalize to 100%
        total_w = sum(sum(row) for row in weights)
        recs = []

        for r in range(3):
            for c in range(3):
                norm_pct = round((weights[r][c] / total_w) * 100.0, 1)
                elem = "background"
                if r == 1 and c == (2 if subject_position == "right" else 0):
                    elem = "face" if has_human_face else "subject"
                elif r == 0:
                    elem = "headline_text"

                grid.append(HeatmapGridCell(r, c, norm_pct, elem))

        if text_word_count > 5:
            recs.append("Reduza o texto da thumbnail para no máximo 4 ou 5 palavras para leitura instantânea em celulares.")
        if not has_human_face:
            recs.append("Adicionar um rosto humano com expressão expressiva pode elevar o CTR em até 30%.")
        if not has_high_contrast:
            recs.append("Aumente a iluminação de contorno (rim light) para destacar o sujeito do fundo.")

        return ThumbnailHeatmapReport(
            overall_ctr_score=min(98, max(20, ctr_score)),
            primary_focal_point=f"Subjeito posicionado à {subject_position.capitalize()}",
            grid_matrix=grid,
            recommendations=recs
        )

