"""
YouTube End Screen Designer for CutWire Drift AI.
Generates 20-second dynamic outro layouts leaving uncluttered visual zones
for YouTube interactive elements (Subscribe circle, Next Best Video card, Playlist).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class EndscreenElementSlot:
    element_type: str  # "subscribe_button", "next_video", "playlist"
    rect_x: int
    rect_y: int
    rect_width: int
    rect_height: int
    label: str

@dataclass
class EndscreenDesignSpec:
    total_duration_sec: float
    slots: List[EndscreenElementSlot]
    background_overlay_style: str
    ffmpeg_overlay_filter: str

class YoutubeEndscreenDesigner:
    """
    Ensures video outros reserve standard YouTube 16:9 interactive target bounds.
    """

    STANDARD_DURATION = 20.0  # Max duration allowed by YouTube for end screens

    @classmethod
    def generate_endscreen_layout(
        cls,
        video_width: int = 1920,
        video_height: int = 1080,
        style: str = "cinematic_minimal"
    ) -> EndscreenDesignSpec:
        # Standard YouTube 1080p coordinate templates
        slots = [
            EndscreenElementSlot("next_video", 120, 320, 680, 382, "Próximo Vídeo Recomendado"),
            EndscreenElementSlot("subscribe_button", 860, 410, 200, 200, "Inscrever-se no Canal"),
            EndscreenElementSlot("playlist", 1120, 320, 680, 382, "Playlist Completa")
        ]

        # Dark gradient vignette on the bottom half so endscreen cards pop
        f_filter = (
            "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.4:t=fill,"
            "drawbox=x=120:y=320:w=680:h=382:color=white@0.2:t=2,"
            "drawbox=x=1120:y=320:w=680:h=382:color=white@0.2:t=2"
        )

        return EndscreenDesignSpec(
            total_duration_sec=cls.STANDARD_DURATION,
            slots=slots,
            background_overlay_style=style,
            ffmpeg_overlay_filter=f_filter
        )

