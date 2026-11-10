"""
Binaural 3D Spatial Audio Panner & 8D Immersion Engine for CutWire Drift AI.
Generates dynamic stereo panning and binaural crossfeed filter expressions for FFmpeg,
moving sound effects and ambient foley seamlessly across left and right audio channels.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class SpatialPanEvent:
    scene_order: int
    pan_trajectory: str  # "left_to_right", "right_to_left", "center_surround", "orbit_8d"
    start_sec: float
    duration_sec: float
    ffmpeg_pan_filter: str
    narrative_justification: str

class BinauralSpatialAudioPanner:
    """
    Builds dynamic 3D audio panning and binaural spatial filters.
    """

    @classmethod
    def calculate_pan_trajectory(cls, scene: Scene) -> str:
        text = (scene.visual_description + " " + (scene.narration_text or "")).lower()

        if any(k in text for k in ["passou", "viaja", "cruza", "movimento", "carro", "nave", "meteoro", "voa"]):
            return "left_to_right" if scene.order % 2 == 1 else "right_to_left"
        elif any(k in text for k in ["universo", "espaço", "galáxia", "atmosfera", "oceano", "vento", "profundo"]):
            return "orbit_8d"
        return "center_surround"

    @classmethod
    def generate_pan_filter(cls, trajectory: str, duration_sec: float) -> str:
        dur = max(duration_sec, 1.0)

        if trajectory == "left_to_right":
            # Smooth left to right linear pan using sine/cosine or pan expressions
            return f"extrastereo=m=1.25,pan=stereo|c0=c0*(1-t/{dur:.2f})|c1=c1*(t/{dur:.2f})"
        elif trajectory == "right_to_left":
            return f"extrastereo=m=1.25,pan=stereo|c0=c0*(t/{dur:.2f})|c1=c1*(1-t/{dur:.2f})"
        elif trajectory == "orbit_8d":
            # Oscillating 8D binaural pan using sine wave
            return f"extrastereo=m=1.35,pan=stereo|c0=c0*(0.5+0.5*cos(2*PI*t/{dur:.2f}))|c1=c1*(0.5+0.5*sin(2*PI*t/{dur:.2f}))"
        else:
            # Subtle wide immersive stereo
            return "extrastereo=m=1.15,stereotools=slev=1.1"

    @classmethod
    def plan_spatial_audio_manifest(cls, plan: ProjectPlan) -> Dict[str, Any]:
        events: List[SpatialPanEvent] = []
        current_time = 0.0

        for scene in plan.scenes:
            dur = max(scene.duration or 3.0, 1.0)
            trajectory = cls.calculate_pan_trajectory(scene)
            filt = cls.generate_pan_filter(trajectory, dur)

            events.append(SpatialPanEvent(
                scene_order=scene.order,
                pan_trajectory=trajectory,
                start_sec=round(current_time, 2),
                duration_sec=round(dur, 2),
                ffmpeg_pan_filter=filt,
                narrative_justification=f"Efeito espacial {trajectory} aplicado para profundidade imersiva de fone de ouvido."
            ))
            current_time += dur

        return {
            "project_id": plan.project_id,
            "total_spatial_events": len(events),
            "binaural_mode": "Cinema 8D Spatial Immersive",
            "events": [e.__dict__ for e in events]
        }
