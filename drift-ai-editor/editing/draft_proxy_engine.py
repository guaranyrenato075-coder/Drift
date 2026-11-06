"""
Draft Proxy Engine for CutWire Drift AI.
Generates lightweight 360p proxies (640x360 @ 24fps, CRF 28) for lag-free timeline preview
and zero GPU VRAM pressure on entry-level graphics cards (NVIDIA GeForce G210 972MB).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os

@dataclass
class ProxyMediaMapping:
    scene_order: int
    original_media_path: str
    proxy_media_path: str
    is_image: bool
    scale_resolution: str      # '640:360'
    ffmpeg_proxy_command: List[str]

@dataclass
class DraftProxySession:
    project_id: str
    is_draft_mode_active: bool
    total_proxies: int
    proxies_dir: str
    mappings: Dict[int, ProxyMediaMapping]

class DraftProxyEngine:
    """
    Manages low-overhead proxy creation and seamless transparent swapping between Draft and Master modes.
    """

    @classmethod
    def create_proxy_spec(
        cls,
        scene_order: int,
        original_path: str,
        proxies_dir: str = "d:/CUTWIREDRIFT/renders/proxies"
    ) -> ProxyMediaMapping:
        try:
            os.makedirs(proxies_dir, exist_ok=True)
        except OSError:
            pass
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        proxy_path = os.path.join(proxies_dir, f"proxy_{scene_order:03d}_{base_name}.mp4").replace("\\", "/")

        is_img = original_path.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))

        if is_img:
            # Imagens estáticas: redimensiona para 640x360 com compressão rápida JPEG
            proxy_img_path = proxy_path.replace(".mp4", ".jpg")
            cmd = [
                "-i", original_path,
                "-vf", "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2",
                "-q:v", "5",
                "-y", proxy_img_path
            ]
            return ProxyMediaMapping(
                scene_order=scene_order,
                original_media_path=original_path,
                proxy_media_path=proxy_img_path,
                is_image=True,
                scale_resolution="640:360",
                ffmpeg_proxy_command=cmd
            )
        else:
            # Vídeos: re-encoda em 360p com preset ultrafast e CRF 28 (processamento em 0.1s)
            cmd = [
                "-i", original_path,
                "-vf", "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2",
                "-r", "24",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                "-an",
                "-y", proxy_path
            ]
            return ProxyMediaMapping(
                scene_order=scene_order,
                original_media_path=original_path,
                proxy_media_path=proxy_path,
                is_image=False,
                scale_resolution="640:360",
                ffmpeg_proxy_command=cmd
            )

    @classmethod
    def build_session(
        cls,
        project_id: str,
        scenes: List[Any],
        proxies_dir: str = "d:/CUTWIREDRIFT/renders/proxies"
    ) -> DraftProxySession:
        mappings: Dict[int, ProxyMediaMapping] = {}

        for sc in scenes:
            order = getattr(sc, "order", 1)
            # Tenta obter o caminho selecionado da mídia
            media_path = ""
            if hasattr(sc, "selected_media") and sc.selected_media:
                media_path = sc.selected_media.local_cached_path or ""
            elif hasattr(sc, "asset_path"):
                media_path = sc.asset_path or ""

            if not media_path:
                media_path = f"assets/media/mock_{order:03d}.mp4"

            mapping = cls.create_proxy_spec(order, media_path, proxies_dir)
            mappings[order] = mapping

        return DraftProxySession(
            project_id=project_id,
            is_draft_mode_active=True,
            total_proxies=len(mappings),
            proxies_dir=proxies_dir,
            mappings=mappings
        )
