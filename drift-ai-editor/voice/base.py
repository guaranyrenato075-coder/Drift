from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
from models.scene_plan import Scene

class BaseVoiceEngine(ABC):
    """Abstract interface for TTS voice engines."""

    @abstractmethod
    def check_status(self) -> Dict[str, Any]:
        """Checks if the engine is ready and returns supported languages."""
        pass

    @abstractmethod
    def list_voices(self) -> List[Dict[str, Any]]:
        """Lists available voice identifiers and names."""
        pass

    @abstractmethod
    def generate_scene(self, scene: Scene, timeout_sec: float = 120.0) -> Scene:
        """
        Generates audio for a single scene and updates its duration and audio path.
        """
        pass

    @abstractmethod
    def generate_sample(self, text: str, voice_id: str, language: str, exaggeration: float = 0.5) -> Dict[str, Any]:
        """Generates a short audio sample for listening."""
        pass

