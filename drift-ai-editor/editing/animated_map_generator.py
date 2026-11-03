"""
Animated Map & Historical Route Generator for CutWire Drift AI.
Detects geographic waypoints and journey descriptions in narrative scripts,
computes 2D/3D trajectory coordinates, and generates motion animation overlays for historical/documentary scenes.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import re

@dataclass
class MapWaypoint:
    city_or_place: str
    latitude: float
    longitude: float

@dataclass
class AnimatedRoutePlan:
    scene_index: int
    origin: MapWaypoint
    destination: MapWaypoint
    travel_type: str  # "land", "maritime", "flight"
    map_style: str    # "vintage_parchment", "satellite", "dark_minimal"
    duration_seconds: float
    svg_route_path: str
    camera_pan_keyframes: List[Dict[str, float]]

class AnimatedMapGenerator:
    """
    Translates textual travel and territorial movements into dynamic map overlays.
    """

    KNOWN_COORDINATES: Dict[str, Tuple[float, float]] = {
        "roma": (41.9028, 12.4964),
        "rome": (41.9028, 12.4964),
        "berlim": (52.5200, 13.4050),
        "berlin": (52.5200, 13.4050),
        "paris": (48.8566, 2.3522),
        "londres": (51.5074, -0.1278),
        "london": (51.5074, -0.1278),
        "lisboa": (38.7223, -9.1393),
        "lisbon": (38.7223, -9.1393),
        "brasilia": (-15.8267, -47.9218),
        "nova york": (40.7128, -74.0060),
        "new york": (40.7128, -74.0060),
        "toquio": (35.6762, 139.6503),
        "tokyo": (35.6762, 139.6503)
    }

    ROUTE_PATTERN = re.compile(r'(?:de|from)\s+([a-zA-Z\s]+?)\s+(?:para|a|até|to)\s+([a-zA-Z\s]+)', re.IGNORECASE)

    @classmethod
    def detect_and_generate_route(cls, scene_index: int, narration_text: str, duration: float = 4.0) -> Optional[AnimatedRoutePlan]:
        match = cls.ROUTE_PATTERN.search(narration_text)
        if not match:
            return None

        orig_raw = match.group(1).strip().lower()
        dest_raw = match.group(2).strip().lower()

        orig_key = next((k for k in cls.KNOWN_COORDINATES if k in orig_raw), orig_raw.split()[0] if orig_raw else "paris")
        dest_key = next((k for k in cls.KNOWN_COORDINATES if k in dest_raw), dest_raw.split()[0] if dest_raw else "berlim")

        orig_coords = cls.KNOWN_COORDINATES.get(orig_key, (48.8566, 2.3522))
        dest_coords = cls.KNOWN_COORDINATES.get(dest_key, (52.5200, 13.4050))

        origin_wp = MapWaypoint(orig_key.capitalize(), orig_coords[0], orig_coords[1])
        dest_wp = MapWaypoint(dest_key.capitalize(), dest_coords[0], dest_coords[1])

        # Generate curved SVG path representation
        svg_path = f"M {orig_coords[1]*5+500},{orig_coords[0]*-5+500} Q {(orig_coords[1]+dest_coords[1])*2.5+500},{(orig_coords[0]+dest_coords[0])*-2.5+450} {dest_coords[1]*5+500},{dest_coords[0]*-5+500}"

        keyframes = [
            {"time": 0.0, "progress": 0.0, "zoom": 1.0},
            {"time": round(duration, 2), "progress": 1.0, "zoom": 1.2}
        ]

        return AnimatedRoutePlan(
            scene_index=scene_index,
            origin=origin_wp,
            destination=dest_wp,
            travel_type="land",
            map_style="vintage_parchment",
            duration_seconds=duration,
            svg_route_path=svg_path,
            camera_pan_keyframes=keyframes
        )
