import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class UserPreferenceRecord:
    preferred_transition: str = "crossfade"
    preferred_pacing_bias: float = 1.0          # 0.8: faster cuts, 1.2: slower
    preferred_subtitle_font: str = "Inter"
    preferred_subtitle_size: int = 42
    preferred_voice_gender: str = "neutral"
    auto_ducking_intensity_db: float = -18.0
    prohibited_transitions: List[str] = field(default_factory=lambda: ["wipe_star", "spiral", "flash_white"])
    preferred_providers: List[str] = field(default_factory=lambda: ["pexels", "unsplash", "archive_org"])
    disliked_keywords: List[str] = field(default_factory=lambda: ["cartoons", "oversaturated", "blurry"])
    require_manual_review_for_climax: bool = True
    total_completed_projects: int = 0
    last_updated: float = field(default_factory=time.time)

class ProductionMemoryManager:
    """
    Production Creative Memory:
    Learns non-intrusively from user choices and revisions across editing sessions:
      - Remembers disliked transitions, favored font choices, and typical pacing speeds.
      - Never modifies models or project parameters silently; acts as smart defaults.
      - User can inspect, edit, export, or reset memory at any time.
    """

    def __init__(self, memory_file: Optional[Path] = None):
        if memory_file is None:
            memory_file = Path(__file__).resolve().parent.parent / "storage" / "user_creative_memory.json"
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.preferences = UserPreferenceRecord()
        self._load()

    def _load(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.preferences = UserPreferenceRecord(**{k: v for k, v in data.items() if k in self.preferences.__dataclass_fields__})
            except Exception:
                self.preferences = UserPreferenceRecord()
        else:
            self._save()

    def _save(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self.preferences), f, indent=2, ensure_ascii=False)

    def record_decision(self, decision_type: str, value: Any) -> None:
        """Logs an accepted user decision to update creative preferences."""
        if decision_type == "transition_rejected":
            if value not in self.preferences.prohibited_transitions:
                self.preferences.prohibited_transitions.append(value)
        elif decision_type == "transition_preferred":
            self.preferences.preferred_transition = str(value)
        elif decision_type == "pacing_changed":
            self.preferences.preferred_pacing_bias = float(value)
        elif decision_type == "subtitle_size":
            self.preferences.preferred_subtitle_size = int(value)
        elif decision_type == "project_completed":
            self.preferences.total_completed_projects += 1

        self.preferences.last_updated = time.time()
        self._save()

    def apply_smart_defaults(self, project_config: Any) -> None:
        """Applies remembered preferences to a new project configuration without locking it."""
        if hasattr(project_config, "transition"):
            project_config.transition = self.preferences.preferred_transition
        if hasattr(project_config, "subtitle_font_size"):
            project_config.subtitle_font_size = self.preferences.preferred_subtitle_size

    def reset_memory(self) -> None:
        self.preferences = UserPreferenceRecord()
        self._save()

