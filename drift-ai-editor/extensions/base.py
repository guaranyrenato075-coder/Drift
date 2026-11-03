from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class ExtensionType(str, Enum):
    TTS = "tts"                     # Voice synthesis (Chatterbox, ElevenLabs, EdgeTTS)
    LLM = "llm"                     # Script and semantic director (Ollama, Gemini, OpenAI)
    IMAGE_GEN = "image_generation"  # AI visual generator (ComfyUI, Stable Diffusion, Midjourney)
    VIDEO_GEN = "video_generation"  # AI motion/video generator (Runway, Kling, Luma)
    TRANSCRIBER = "transcriber"     # Speech-to-text (Whisper, FasterWhisper)

@dataclass
class ExtensionManifest:
    extension_id: str
    extension_type: ExtensionType
    name: str
    version: str
    author: str
    description: str
    is_local: bool = True           # Runs on device without internet
    requires_api_key: bool = False
    required_env_vars: List[str] = field(default_factory=list)
    hardware_requirements: Dict[str, Any] = field(default_factory=dict) # e.g. {'gpu_vram_gb': 6}

class BaseAiExtension(ABC):
    """
    Abstract interface for pluggable AI backend providers.
    Enables swapping TTS, LLM, or image generation engines without touching editor core.
    """

    @property
    @abstractmethod
    def manifest(self) -> ExtensionManifest:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if required drivers, models, or API credentials exist."""
        pass

    @abstractmethod
    def execute(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Runs extension task and returns normalized dictionary result."""
        pass

