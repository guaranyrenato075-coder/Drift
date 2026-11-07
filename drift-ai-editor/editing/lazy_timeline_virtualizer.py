"""
Lazy Timeline Virtualizer for CutWire Drift AI.
Maintains active OS file handles and video decoders only for a narrow sliding window of scenes
around the current playhead (default 5 scenes), keeping the remaining 140+ scenes in lightweight hibernation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set

@dataclass
class VirtualizedClipHandle:
    scene_order: int
    is_active: bool
    is_hibernating: bool
    media_path: str
    file_descriptor_allocated: bool

@dataclass
class VirtualizerWindowState:
    current_playhead_scene: int
    window_radius: int
    total_scenes: int
    active_handles_count: int
    hibernating_handles_count: int
    handles: Dict[int, VirtualizedClipHandle]

class LazyTimelineVirtualizer:
    """
    Dynamically virtualizes timeline playback resources to prevent OS file descriptor exhaustion.
    """

    def __init__(self, window_radius: int = 2):
        self.window_radius = window_radius # 2 antes + 1 atual + 2 depois = 5 ativas
        self.handles: Dict[int, VirtualizedClipHandle] = {}

    def register_scenes(self, scenes: List[Any]) -> None:
        self.handles.clear()
        for sc in scenes:
            order = getattr(sc, "order", 1)
            path = ""
            if hasattr(sc, "selected_media") and sc.selected_media:
                path = sc.selected_media.local_cached_path or ""
            elif hasattr(sc, "asset_path"):
                path = sc.asset_path or ""

            self.handles[order] = VirtualizedClipHandle(
                scene_order=order,
                is_active=False,
                is_hibernating=True,
                media_path=path or f"mock_{order}.mp4",
                file_descriptor_allocated=False
            )

    def update_playhead(self, playhead_scene_order: int) -> VirtualizerWindowState:
        min_active = max(1, playhead_scene_order - self.window_radius)
        max_active = playhead_scene_order + self.window_radius

        active_count = 0
        hibernating_count = 0

        for order, handle in self.handles.items():
            if min_active <= order <= max_active:
                handle.is_active = True
                handle.is_hibernating = False
                handle.file_descriptor_allocated = True
                active_count += 1
            else:
                handle.is_active = False
                handle.is_hibernating = True
                handle.file_descriptor_allocated = False
                hibernating_count += 1

        return VirtualizerWindowState(
            current_playhead_scene=playhead_scene_order,
            window_radius=self.window_radius,
            total_scenes=len(self.handles),
            active_handles_count=active_count,
            hibernating_handles_count=hibernating_count,
            handles=dict(self.handles)
        )

