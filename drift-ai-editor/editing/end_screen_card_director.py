"""
Automated YouTube End-Screen Card & Outro Director for CutWire Drift AI.
Generates a polished 15-20 second cinematic outro sequence with dedicated placeholder zones
for native YouTube Studio End Screen elements (Next Video, Playlist, Subscribe Avatar) and CTA audio fade.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import ProjectPlan

@dataclass
class EndScreenTemplate:
    duration_sec: float
    video_recommendation_box: str  # "top_right", "top_left", etc.
    subscribe_avatar_pos: str
    cta_headline_text: str
    music_fade_duration_sec: float
    ffmpeg_outro_filter: str

class AIAutomatedEndScreenCardDirector:
    """
    Directs closing card sequences tailored to boost YouTube subscriber conversion and binge-watching.
    """

    @classmethod
    def generate_outro_template(
        cls,
        plan: ProjectPlan,
        duration_sec: float = 18.0,
        width: int = 1920,
        height: int = 1080
    ) -> EndScreenTemplate:
        cta_text = "SE GOSTOU, ASSISTA A ESTE PRÓXIMO DOCUMENTÁRIO:"

        # YouTube End Screen Safe Zone Boxes:
        # Video box 16:9 on right: x=w-720-80, y=140, w=720, h=405
        # Subscribe circle on left: x=180, y=h/2-100, radius=90
        video_box_w = int(width * 0.38)
        video_box_h = int(video_box_w * 9 / 16)
        video_x = width - video_box_w - 80
        video_y = int((height - video_box_h) / 2)

        box_filter = (
            f"drawbox=x={video_x}:y={video_y}:w={video_box_w}:h={video_box_h}:"
            f"color=white@0.2:t=fill,"
            f"drawbox=x={video_x}:y={video_y}:w={video_box_w}:h={video_box_h}:"
            f"color=gold@0.8:t=4"
        )

        avatar_x = 180
        avatar_y = int(height / 2 - 80)
        avatar_filter = (
            f"drawbox=x={avatar_x}:y={avatar_y}:w=160:h=160:color=cyan@0.7:t=4"
        )

        title_filter = (
            f"drawtext=text='{cta_text}':fontcolor=white@0.9:fontsize=32:"
            f"x=(w-text_w)/2:y=60:shadowcolor=black@0.8:shadowx=2:shadowy=2"
        )

        outro_filter = f"{box_filter},{avatar_filter},{title_filter}"

        return EndScreenTemplate(
            duration_sec=duration_sec,
            video_recommendation_box=f"x={video_x}, y={video_y}, w={video_box_w}, h={video_box_h}",
            subscribe_avatar_pos=f"x={avatar_x}, y={avatar_y}, size=160x160",
            cta_headline_text=cta_text,
            music_fade_duration_sec=3.0,
            ffmpeg_outro_filter=outro_filter
        )

    @classmethod
    def plan_end_screen(cls, plan: ProjectPlan) -> Dict[str, Any]:
        tmpl = cls.generate_outro_template(plan, width=plan.config.width, height=plan.config.height)
        return {
            "project_id": plan.project_id,
            "end_screen_duration_sec": tmpl.duration_sec,
            "cta_headline": tmpl.cta_headline_text,
            "youtube_box_coordinates": tmpl.video_recommendation_box,
            "subscribe_coordinates": tmpl.subscribe_avatar_pos,
            "ffmpeg_outro_filter": tmpl.ffmpeg_outro_filter,
            "youtube_studio_ready": True
        }
