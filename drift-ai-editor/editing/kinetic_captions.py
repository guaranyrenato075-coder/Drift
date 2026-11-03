"""
Kinetic Word-by-Word Subtitle Engine for CutWire Drift AI.
Generates animated ASS/SRT caption styling styled like top viral creators (Hormozi, MrBeast),
featuring dynamic word highlighting (yellow/green), auto emoji anchors, and elastic bounce scale tags.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re

@dataclass
class KineticWordCue:
    word: str
    start_time: float
    end_time: float
    is_highlighted: bool
    highlight_color: str  # e.g., "#FFEE00"
    attached_emoji: Optional[str] = None

@dataclass
class KineticSubtitleBlock:
    scene_order: int
    full_text: str
    word_cues: List[KineticWordCue]
    ass_dialogue_line: str

class KineticCaptionsEngine:
    """
    Synthesizes frame-perfect pop-in word animations for vertical Shorts.
    """

    EMOJI_TRIGGERS: Dict[str, str] = {
        "fogo": "🔥", "fire": "🔥",
        "dinheiro": "💰", "money": "💰",
        "ideia": "💡", "idea": "💡",
        "foguete": "🚀", "rocket": "🚀",
        "segredo": "🤫", "secret": "🤫",
        "erro": "❌", "error": "❌",
        "certo": "✅", "win": "✅",
        "choque": "⚡", "shock": "⚡",
        "cérebro": "🧠", "mente": "🧠"
    }

    HIGHLIGHT_WORDS = {"nunca", "sempre", "dinheiro", "segredo", "poder", "essencial", "perigo", "verdade", "transformou"}

    @classmethod
    def generate_kinetic_block(
        cls,
        scene_order: int,
        narration_text: str,
        start_time: float,
        duration: float
    ) -> KineticSubtitleBlock:
        words = narration_text.strip().split()
        if not words:
            return KineticSubtitleBlock(scene_order, "", [], "")

        word_dur = duration / len(words)
        cues: List[KineticWordCue] = []

        ass_parts = []
        for i, w in enumerate(words):
            w_clean = re.sub(r'[^\w\s]', '', w.lower())
            w_start = start_time + (i * word_dur)
            w_end = w_start + word_dur

            is_highlight = w_clean in cls.HIGHLIGHT_WORDS
            emoji = cls.EMOJI_TRIGGERS.get(w_clean, None)
            color = "#00FF66" if is_highlight else "#FFEE00"

            cues.append(
                KineticWordCue(
                    word=w,
                    start_time=round(w_start, 2),
                    end_time=round(w_end, 2),
                    is_highlighted=is_highlight,
                    highlight_color=color,
                    attached_emoji=emoji
                )
            )

            # Generate ASS tag for bounce animation
            display_word = f"{w} {emoji}" if emoji else w
            if is_highlight:
                ass_parts.append(f"{{\\c&H00FFEE&\\t(0,100,\\fscx115\\fscy115)}}{display_word}{{\\r}}")
            else:
                ass_parts.append(f"{{\\c&HFFFFFF&}}{display_word}{{\\r}}")

        ass_line = " ".join(ass_parts)

        return KineticSubtitleBlock(
            scene_order=scene_order,
            full_text=narration_text,
            word_cues=cues,
            ass_dialogue_line=ass_line
        )

