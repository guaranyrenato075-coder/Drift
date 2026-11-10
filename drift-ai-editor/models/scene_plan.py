from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid
import time


class SceneState(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    VOICE_GENERATING = "voice_generating"
    SEARCHING = "searching"
    SELECTING = "selecting"
    DOWNLOADING = "downloading"
    READY = "ready"
    PLACED = "placed"
    ERROR = "error"


@dataclass
class Provenance:
    platform: str = ""
    item_id: str = ""
    page_url: str = ""
    creator: str = ""
    license: str = ""
    fetch_date: str = ""
    query: str = ""
    local_path: str = ""
    width: int = 0
    height: int = 0
    duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Provenance:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class MediaCandidate:
    candidate_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = ""
    media_type: str = "video"  # "video" or "image"
    external_id: str = ""
    title: str = ""
    preview_url: str = ""
    download_url: str = ""
    creator: str = ""
    page_url: str = ""
    license: str = ""
    width: int = 0
    height: int = 0
    duration: float = 0.0
    aspect_ratio: str = "16:9"
    local_cached_path: Optional[str] = None
    score: float = 0.0
    copyright_risk: str = "safe"  # "safe", "attribution_required", "restricted"
    commercial_use: bool = True
    attribution_text: Optional[str] = None
    content_id_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MediaCandidate:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Scene:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order: int = 1
    narration_text: str = ""
    visual_description: str = ""
    concept: str = ""
    visual_intent: Optional[Dict[str, Any]] = None
    keywords: List[str] = field(default_factory=list)
    english_keywords: List[str] = field(default_factory=list)
    
    # Timing (in seconds)
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    
    # Audio fields
    language: str = "pt"
    voice_id: str = "default"
    audio_path: Optional[str] = None
    audio_job_id: Optional[str] = None
    audio_duration: float = 0.0
    exaggeration: float = 0.5
    
    # Visual search & selection
    candidates: List[MediaCandidate] = field(default_factory=list)
    selected_media: Optional[MediaCandidate] = None
    provenance: Optional[Provenance] = None
    
    # Timeline link
    timeline_clip_id: Optional[str] = None
    
    # Lifecycle
    state: SceneState = SceneState.PENDING
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["state"] = self.state.value
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Scene:
        candidates_raw = data.get("candidates", [])
        candidates = [MediaCandidate.from_dict(c) if isinstance(c, dict) else c for c in candidates_raw]
        
        sel_media_raw = data.get("selected_media")
        selected_media = MediaCandidate.from_dict(sel_media_raw) if isinstance(sel_media_raw, dict) else sel_media_raw
        
        prov_raw = data.get("provenance")
        provenance = Provenance.from_dict(prov_raw) if isinstance(prov_raw, dict) else prov_raw

        state_val = data.get("state", SceneState.PENDING)
        if isinstance(state_val, str):
            try:
                state = SceneState(state_val)
            except ValueError:
                state = SceneState.PENDING
        else:
            state = state_val

        fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        fields["candidates"] = candidates
        fields["selected_media"] = selected_media
        fields["provenance"] = provenance
        fields["state"] = state
        return cls(**fields)


@dataclass
class ProjectConfig:
    aspect_ratio: str = "16:9"  # "16:9", "9:16", "1:1"
    media_type: str = "all"      # "all", "video", "image"
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    style: str = "cinematographic"  # "cinematographic", "documentary", "dynamic", "minimalist"
    language: str = "pt"
    voice_id: str = "default"
    exaggeration: float = 0.5
    sources: List[str] = field(default_factory=lambda: ["pexels", "pixabay", "wikimedia", "nasa"])
    enable_subtitles: bool = True
    enable_ken_burns: bool = True
    transition_kind: str = "crossfade"  # "none", "crossfade", "luma_fade", "dip"
    background_music: bool = False
    background_music_path: Optional[str] = None
    auto_ducking: bool = True
    music_volume: float = 0.15
    extra: Dict[str, Any] = field(default_factory=dict)

    def update_resolution(self):
        if self.aspect_ratio == "9:16":
            self.width, self.height = 1080, 1920
        elif self.aspect_ratio == "1:1":
            self.width, self.height = 1080, 1080
        else:
            self.width, self.height = 1920, 1080

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ProjectPlan:
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Novo Projeto IA"
    raw_script: str = ""
    config: ProjectConfig = field(default_factory=ProjectConfig)
    scenes: List[Scene] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def total_duration(self) -> float:
        return sum(s.duration for s in self.scenes)

    def reindex_scenes(self):
        current_time = 0.0
        for idx, scene in enumerate(self.scenes, start=1):
            scene.order = idx
            scene.start_time = current_time
            if scene.duration > 0:
                scene.end_time = current_time + scene.duration
                current_time = scene.end_time
            else:
                scene.end_time = current_time
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "raw_script": self.raw_script,
            "config": self.config.to_dict(),
            "scenes": [s.to_dict() for s in self.scenes],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectPlan:
        config_data = data.get("config", {})
        config = ProjectConfig.from_dict(config_data) if isinstance(config_data, dict) else ProjectConfig()
        scenes_data = data.get("scenes", [])
        scenes = [Scene.from_dict(s) if isinstance(s, dict) else s for s in scenes_data]
        
        return cls(
            project_id=data.get("project_id", str(uuid.uuid4())),
            title=data.get("title", "Novo Projeto IA"),
            raw_script=data.get("raw_script", ""),
            config=config,
            scenes=scenes,
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )

