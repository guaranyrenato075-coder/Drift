"""
Módulo de Escalonador Inteligente de Resolução de Proxies (Smart Proxy Resolution Scaler).
Calcula matrizes de reamostragem rápida (downsampling bilinear) para pré-visualização
instantânea de clipes na timeline. Substitui decodificações pesadas de vídeo em 4K e 1080p
por fluxos otimizados em 540p durante o rascunho, reduzindo em mais de 70% o consumo de RAM/VRAM.
"""

from typing import Dict, Any, Tuple


class SmartProxyResolutionScaler:
    """
    Gerador e dimensionador de proxies ultraleves para economia drástica de memória gráfica e RAM.
    """

    PREVIEW_TIERS = {
        "ultra_light_540p": {
            "name": "540p Ultra-Light (Máxima Fluidez e Mínima RAM)",
            "width": 960,
            "height": 540,
            "bitrate_k": 800,
            "ram_saving_vs_1080p_pct": 75.0,
            "vram_saving_vs_4k_pct": 93.7
        },
        "balanced_720p": {
            "name": "720p HD Balanceado",
            "width": 1280,
            "height": 720,
            "bitrate_k": 1500,
            "ram_saving_vs_1080p_pct": 55.5,
            "vram_saving_vs_4k_pct": 88.9
        },
        "full_master_1080p": {
            "name": "1080p Full HD (Exportação Master)",
            "width": 1920,
            "height": 1080,
            "bitrate_k": 8000,
            "ram_saving_vs_1080p_pct": 0.0,
            "vram_saving_vs_4k_pct": 75.0
        }
    }

    @classmethod
    def calculate_proxy_scaling(
        cls,
        source_width: int,
        source_height: int,
        tier: str = "ultra_light_540p"
    ) -> Dict[str, Any]:
        """
        Calcula os parâmetros de escala e o filtro FFmpeg de redimensionamento rápido.
        """
        config = cls.PREVIEW_TIERS.get(tier, cls.PREVIEW_TIERS["ultra_light_540p"])
        target_w = config["width"]
        target_h = config["height"]

        # Calcula aspect ratio proporcional
        aspect = source_width / max(source_height, 1)
        if aspect >= 1.7:  # Widescreen 16:9
            final_w, final_h = target_w, target_h
        elif aspect <= 0.6:  # Vertical 9:16 (Shorts/Reels)
            final_w, final_h = target_h, target_w
        else:
            final_w = int((target_h * aspect) // 2) * 2
            final_h = target_h

        # Flags para decodificação e escala ultrarrápidas (bilinear sem overhead de bicubic)
        scale_filter = f"scale={final_w}:{final_h}:flags=bilinear"

        return {
            "status": "success",
            "tier_applied": tier,
            "tier_name": config["name"],
            "source_resolution": f"{source_width}x{source_height}",
            "proxy_resolution": f"{final_w}x{final_h}",
            "ffmpeg_scale_filter": scale_filter,
            "recommended_bitrate": f"{config['bitrate_k']}k",
            "ram_reduction_pct": config["ram_saving_vs_1080p_pct"],
            "vram_reduction_pct": config["vram_saving_vs_4k_pct"],
            "summary": (
                f"Modo proxy ativo ({final_w}x{final_h}): economia estimada de {config['ram_saving_vs_1080p_pct']}% "
                f"de memória RAM em relação à resolução nativa."
            )
        }
