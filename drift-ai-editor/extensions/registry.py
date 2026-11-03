import logging
from typing import Dict, Any, List, Optional
from extensions.base import BaseAiExtension, ExtensionType, ExtensionManifest

logger = logging.getLogger("drift.extensions.registry")

class ExtensionRegistry:
    """
    Central discovery and management catalog for AI provider adapters.
    Maintains active and fallback backends for TTS, LLM, Image Generation, etc.
    """

    def __init__(self):
        self._extensions: Dict[str, BaseAiExtension] = {}
        self._active_by_type: Dict[ExtensionType, str] = {}

    def register(self, extension: BaseAiExtension, set_as_active: bool = True) -> None:
        m = extension.manifest
        self._extensions[m.extension_id] = extension
        logger.info(f"Registrada extensão IA: [{m.extension_type.value}] {m.name} (v{m.version})")
        if set_as_active or m.extension_type not in self._active_by_type:
            self._active_by_type[m.extension_type] = m.extension_id

    def get_extension(self, extension_id: str) -> Optional[BaseAiExtension]:
        return self._extensions.get(extension_id)

    def get_active(self, ext_type: ExtensionType) -> Optional[BaseAiExtension]:
        ext_id = self._active_by_type.get(ext_type)
        if ext_id and ext_id in self._extensions:
            ext = self._extensions[ext_id]
            if ext.is_available():
                return ext
        # Fallback to any available extension of the same type
        for ext in self._extensions.values():
            if ext.manifest.extension_type == ext_type and ext.is_available():
                return ext
        return None

    def list_extensions(self, filter_type: Optional[ExtensionType] = None) -> List[Dict[str, Any]]:
        result = []
        for ext_id, ext in self._extensions.items():
            m = ext.manifest
            if filter_type and m.extension_type != filter_type:
                continue
            is_active = self._active_by_type.get(m.extension_type) == ext_id
            result.append({
                "extension_id": m.extension_id,
                "type": m.extension_type.value,
                "name": m.name,
                "version": m.version,
                "is_local": m.is_local,
                "is_available": ext.is_available(),
                "is_active": is_active,
                "description": m.description
            })
        return result

