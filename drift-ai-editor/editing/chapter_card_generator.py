"""
Automated Video Chapter Card & Title Sequence Generator for CutWire Drift AI.
Generates cinematic motion graphic transition cards between long-form chapters,
featuring Roman numeral indexation, elegant typography, and deep sub-boom impact foley.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import ProjectPlan

@dataclass
class ChapterTitleCard:
    chapter_index: int
    roman_numeral: str
    chapter_title: str
    card_duration_sec: float
    ffmpeg_drawtext_filter: str
    foley_sound_effect: str

class AutoVideoChapterCardGenerator:
    """
    Builds chapter divider sequences for documentary and long-form productions.
    """

    ROMAN_MAP = {
        1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
        6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"
    }

    @classmethod
    def generate_chapter_card(
        cls,
        index: int,
        title: str,
        duration: float = 3.0,
        width: int = 1920,
        height: int = 1080
    ) -> ChapterTitleCard:
        roman = cls.ROMAN_MAP.get(index, str(index))
        clean_title = title.replace("'", "\\'").upper()

        # Build FFmpeg filter: dark solid background with gold/white centered text
        roman_filter = (
            f"drawtext=text='CAPÍTULO {roman}':fontcolor=gold@0.9:fontsize=38:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-50:shadowcolor=black@0.8:shadowx=3:shadowy=3"
        )
        title_filter = (
            f"drawtext=text='{clean_title}':fontcolor=white@0.95:fontsize=52:"
            f"x=(w-text_w)/2:y=(h-text_h)/2+30:shadowcolor=black@0.9:shadowx=4:shadowy=4"
        )
        full_filter = f"{roman_filter},{title_filter}"

        return ChapterTitleCard(
            chapter_index=index,
            roman_numeral=roman,
            chapter_title=title,
            card_duration_sec=duration,
            ffmpeg_drawtext_filter=full_filter,
            foley_sound_effect="cinematic_sub_boom_whoosh.wav"
        )

    @classmethod
    def generate_cards_for_plan(cls, plan: ProjectPlan) -> Dict[str, Any]:
        extra = plan.config.extra or {}
        chapter_titles = extra.get("chapter_titles") or [
            "A Origem e os Primeiros Sinais",
            "O Desenvolvimento dos Acontecimentos",
            "O Clímax da Revelação",
            "O Legado e a Conclusão Final"
        ]

        cards = [
            cls.generate_chapter_card(
                index=idx + 1,
                title=t,
                duration=3.0,
                width=plan.config.width,
                height=plan.config.height
            )
            for idx, t in enumerate(chapter_titles)
        ]

        return {
            "project_id": plan.project_id,
            "total_chapter_cards": len(cards),
            "cards": [c.__dict__ for c in cards]
        }
