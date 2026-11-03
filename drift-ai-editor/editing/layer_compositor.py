from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import uuid

class LayerType(str, Enum):
    BACKGROUND = "background"
    MEDIA_CLIP = "media_clip"
    MASKED_FOREGROUND = "masked_foreground"
    LOWER_THIRD = "lower_third"
    KINETIC_TITLE = "kinetic_title"
    GRAPHIC_ACCENT = "graphic_accent"
    PARTICLE_OVERLAY = "particle_overlay"

class BlendMode(str, Enum):
    NORMAL = "normal"
    SCREEN = "screen"
    MULTIPLY = "multiply"
    OVERLAY = "overlay"
    ADD = "add"

@dataclass
class LayerSpec:
    layer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    layer_type: LayerType = LayerType.MEDIA_CLIP
    track_index: int = 0             # 0: V1 (base), 1: V2 (b-roll), 2: V3 (graphics)
    source_path: str = ""
    opacity: float = 1.0             # 0.0 to 1.0
    scale: float = 1.0
    position_x: float = 0.0          # Centered offset in pixels
    position_y: float = 0.0
    blend_mode: BlendMode = BlendMode.NORMAL
    animation_in: Optional[str] = "fade_in"    # 'fade_in', 'slide_up', 'zoom_in'
    animation_out: Optional[str] = "fade_out"
    content_text: Optional[str] = None         # For titles/kinetic lower thirds
    is_locked: bool = False                    # Protect from AI re-renders

@dataclass
class MultiLayerScene:
    scene_order: int
    duration_sec: float
    layers: List[LayerSpec] = field(default_factory=list)

class LayerCompositor:
    """
    Advanced Multi-Layer Scene Compositor:
    Constructs sophisticated scenes combining background footage, foreground cutouts,
    kinetic titles, lower-thirds, and visual particle overlays across independent Drift tracks.
    Allows changing background media without losing title positioning or graphics.
    """

    @classmethod
    def compose_scene(
        cls,
        scene_order: int,
        duration_sec: float,
        background_media_path: str,
        title_text: Optional[str] = None,
        include_lower_third: bool = False,
        particle_overlay_path: Optional[str] = None
    ) -> MultiLayerScene:
        layers: List[LayerSpec] = []

        # Layer 1: Background Video/Photo (Track 0 / V1)
        layers.append(
            LayerSpec(
                layer_type=LayerType.BACKGROUND,
                track_index=0,
                source_path=background_media_path,
                opacity=1.0,
                scale=1.0,
                blend_mode=BlendMode.NORMAL,
                animation_in="crossfade"
            )
        )

        # Layer 2: Particle / Light Texture Overlay (Track 1 / V2)
        if particle_overlay_path:
            layers.append(
                LayerSpec(
                    layer_type=LayerType.PARTICLE_OVERLAY,
                    track_index=1,
                    source_path=particle_overlay_path,
                    opacity=0.35,
                    scale=1.0,
                    blend_mode=BlendMode.SCREEN
                )
            )

        # Layer 3: Kinetic Title / Lower-Third (Track 2 / V3)
        if title_text:
            l_type = LayerType.LOWER_THIRD if include_lower_third else LayerType.KINETIC_TITLE
            layers.append(
                LayerSpec(
                    layer_type=l_type,
                    track_index=2,
                    content_text=title_text,
                    opacity=1.0,
                    position_y=360 if include_lower_third else 0.0, # Lower-third or centered
                    animation_in="slide_up",
                    animation_out="fade_out"
                )
            )

        return MultiLayerScene(
            scene_order=scene_order,
            duration_sec=duration_sec,
            layers=layers
        )

    @classmethod
    def replace_background(cls, composite: MultiLayerScene, new_background_path: str) -> None:
        """Swaps only the background layer, keeping titles and graphics 100% intact."""
        for layer in composite.layers:
            if layer.layer_type in (LayerType.BACKGROUND, LayerType.MEDIA_CLIP) and layer.track_index == 0:
                if not layer.is_locked:
                    layer.source_path = new_background_path
                break

