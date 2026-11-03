"""
Quote Card Popup & Typography Callout Engine for CutWire Drift AI.
Generates stylized motion cards for philosophical quotes, historical statements,
data facts, or book excerpts with author attribution and smooth entry animations.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class QuoteCardSpec:
    quote_text: str
    author: str
    source_work: Optional[str]
    start_sec: float
    duration_sec: float
    card_theme: str            # 'minimal_dark', 'parchment_gold', 'cyber_neon'
    ffmpeg_complex_filter: str

class QuoteCardPopup:
    """
    Renders high-aesthetic quotation cards over video backgrounds.
    """

    THEME_COLORS = {
        "minimal_dark": {"bg": "black@0.75", "quote_color": "white", "author_color": "#AAAAAA"},
        "parchment_gold": {"bg": "#1e1810@0.85", "quote_color": "#F3E5AB", "author_color": "#D4AF37"},
        "cyber_neon": {"bg": "#0a0a1f@0.85", "quote_color": "#00FFCC", "author_color": "#FF007F"},
    }

    @classmethod
    def create_quote_card(
        cls,
        quote_text: str,
        author: str,
        source_work: Optional[str] = None,
        start_sec: float = 0.5,
        duration_sec: float = 4.0,
        theme: str = "minimal_dark"
    ) -> QuoteCardSpec:
        palette = cls.THEME_COLORS.get(theme, cls.THEME_COLORS["minimal_dark"])
        end_sec = start_sec + duration_sec
        source_label = f" ({source_work})" if source_work else ""
        escaped_quote = quote_text.replace("'", "\\'").replace(":", "\\:")
        escaped_author = f"- {author}{source_label}".replace("'", "\\'").replace(":", "\\:")

        # Animated slide-up and fade box + quote + author
        filter_chain = (
            f"drawbox=y=ih*0.65:h=ih*0.25:color={palette['bg']}:t=fill:"
            f"enable='between(t,{start_sec},{end_sec})',"
            f"drawtext=text='\"{escaped_quote}\"':fontsize=28:fontcolor={palette['quote_color']}:"
            f"x=(w-text_w)/2:y=ih*0.70:enable='between(t,{start_sec},{end_sec})',"
            f"drawtext=text='{escaped_author}':fontsize=20:fontcolor={palette['author_color']}:"
            f"x=(w-text_w)/2:y=ih*0.80:enable='between(t,{start_sec},{end_sec})'"
        )

        return QuoteCardSpec(
            quote_text=quote_text,
            author=author,
            source_work=source_work,
            start_sec=start_sec,
            duration_sec=duration_sec,
            card_theme=theme,
            ffmpeg_complex_filter=filter_chain
        )

