"""
Smart Ken Burns and Dynamic Punch-In Filter Engine for CutWire Drift AI.
Generates automated camera motion for still images and dynamic emphasis punch-ins
(1.10x scale cuts) on pivotal phrases to eliminate visual monotony in long videos.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import math

@dataclass
class VisualMotionEffect:
    scene_order: int
    is_still_image: bool
    motion_type: str        # 'ken_burns_zoom_in', 'ken_burns_zoom_out', 'ken_burns_pan_left', 'punch_in_emphasis', 'static_stabilized'
    start_scale: float
    end_scale: float
    duration_sec: float
    ffmpeg_video_filter: str

class SmartKenBurnsPunchInEngine:
    """
    Transforms static media and key narration moments into dynamic, cinematic camera movements.
    """

    MOTION_PATTERNS = [
        "ken_burns_zoom_in",
        "ken_burns_pan_right",
        "ken_burns_zoom_out",
        "ken_burns_pan_left"
    ]

    @classmethod
    def generate_effect(
        cls,
        scene_order: int,
        duration_sec: float,
        is_still_image: bool = True,
        is_key_emphasis: bool = False,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30
    ) -> VisualMotionEffect:
        dur = max(0.5, duration_sec)
        total_frames = int(dur * fps)

        # 1. Se for um momento de ênfase dramática (Punch-in instantâneo de 1.10x)
        if is_key_emphasis:
            # Crop centralizado com escala 1.10x
            crop_w = int(width / 1.10)
            crop_h = int(height / 1.10)
            crop_x = int((width - crop_w) / 2)
            crop_y = int((height - crop_h) / 2)
            
            # Filtro FFmpeg para punch-in instantâneo
            ff_filter = f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={width}:{height}"
            return VisualMotionEffect(
                scene_order=scene_order,
                is_still_image=is_still_image,
                motion_type="punch_in_emphasis",
                start_scale=1.10,
                end_scale=1.10,
                duration_sec=dur,
                ffmpeg_video_filter=ff_filter
            )

        # 2. Se for imagem estática, aplica Ken Burns contínuo e suave
        if is_still_image:
            pattern = cls.MOTION_PATTERNS[(scene_order - 1) % len(cls.MOTION_PATTERNS)]
            
            if pattern == "ken_burns_zoom_in":
                # Zoom suave de 1.0 para 1.15
                ff_filter = f"zoompan=z='min(zoom+0.0015,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
                start_scale = 1.0
                end_scale = 1.15
            elif pattern == "ken_burns_zoom_out":
                # Começa em 1.15 e faz zoom out suave para 1.0
                ff_filter = f"zoompan=z='if(lte(zoom,1.0),1.15,max(1.001,zoom-0.0015))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
                start_scale = 1.15
                end_scale = 1.0
            elif pattern == "ken_burns_pan_right":
                # Pan lento da esquerda para a direita com leve zoom de 1.08
                ff_filter = f"zoompan=z='1.08':x='if(lte(on,1),(iw-iw/zoom)/2,x+1)':y='(ih-ih/zoom)/2':d={total_frames}:s={width}x{height}:fps={fps}"
                start_scale = 1.08
                end_scale = 1.08
            else: # pan_left
                # Pan lento da direita para a esquerda
                ff_filter = f"zoompan=z='1.08':x='if(lte(on,1),(iw-iw/zoom),max(0,x-1))':d={total_frames}:s={width}x{height}:fps={fps}"
                start_scale = 1.08
                end_scale = 1.08

            return VisualMotionEffect(
                scene_order=scene_order,
                is_still_image=True,
                motion_type=pattern,
                start_scale=start_scale,
                end_scale=end_scale,
                duration_sec=dur,
                ffmpeg_video_filter=ff_filter
            )

        # 3. Se já for um vídeo animado, mantém proporção e estabiliza
        return VisualMotionEffect(
            scene_order=scene_order,
            is_still_image=False,
            motion_type="static_stabilized",
            start_scale=1.0,
            end_scale=1.0,
            duration_sec=dur,
            ffmpeg_video_filter=f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        )

    @classmethod
    def apply_to_project_scenes(
        cls,
        scenes: List[Dict[str, Any]],
        width: int = 1920,
        height: int = 1080
    ) -> List[VisualMotionEffect]:
        effects = []
        for s in scenes:
            order = s.get("order", 1)
            dur = s.get("duration", 5.0)
            is_still = s.get("media_type", "image") == "image"
            is_emphasis = "hook" in str(s.get("tags", [])) or s.get("is_key_point", False)

            eff = cls.generate_effect(
                scene_order=order,
                duration_sec=dur,
                is_still_image=is_still,
                is_key_emphasis=is_emphasis,
                width=width,
                height=height
            )
            effects.append(eff)
        return effects

