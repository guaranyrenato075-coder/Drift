from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.scene_plan import MediaCandidate, Provenance

class BaseMediaProvider(ABC):
    """Abstract interface for video media stock providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'pexels', 'pixabay', 'wikimedia', 'nasa')."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        """
        Searches the provider for matching video clips or images and normalizes results
        into MediaCandidate instances. media_type can be 'all', 'video', or 'image'.
        """
        pass

