"""
Auto Color Tone Film Stock Emulator.
Emulador de perfis de película cinematográfica analógica (Kodak Vision3, Fujifilm Eterna,
Technicolor 3-Strip, Bleach Bypass, Cinema Noir) via curvas FFmpeg e granulação estocástica.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class AutoColorToneFilmStockEmulator:
    """Aplica características de película cinematográfica e curvas analógicas."""

    FILM_STOCKS = {
        "kodak_vision3_5219": {
            "name": "Kodak Vision3 5219 (Tungsten)",
            "description": "Tons de pele orgânicos, sombras quentes douradas e alta latitude de exposição.",
            "contrast": 1.15,
            "saturation": 1.1,
            "gamma": 0.98,
            "grain_default": 12,
            "color_temperature": "warm",
            "ffmpeg_curves": "curves=all='0/0 0.5/0.48 1/1':red='0/0 0.5/0.53 1/1':blue='0/0 0.5/0.46 1/1'"
        },
        "fujifilm_eterna": {
            "name": "Fujifilm Eterna 250D",
            "description": "Cores suaves pastéis, baixa saturação nas sombras, verdes profundos e visual indie poético.",
            "contrast": 1.05,
            "saturation": 0.88,
            "gamma": 1.05,
            "grain_default": 8,
            "color_temperature": "neutral_soft",
            "ffmpeg_curves": "curves=all='0/0.04 0.5/0.5 1/0.95':green='0/0 0.5/0.52 1/1'"
        },
        "technicolor_3strip": {
            "name": "Technicolor 3-Strip (Golden Era)",
            "description": "Vermelhos e azuis hiper-vibrantes, alto contraste histórico dos clássicos de Hollywood dos anos 40/50.",
            "contrast": 1.35,
            "saturation": 1.45,
            "gamma": 0.92,
            "grain_default": 15,
            "color_temperature": "vibrant_classic",
            "ffmpeg_curves": "curves=red='0/0 0.3/0.38 0.7/0.8 1/1':green='0/0 0.5/0.47 1/1':blue='0/0 0.5/0.55 1/1'"
        },
        "bleach_bypass": {
            "name": "Bleach Bypass (Silver Retention)",
            "description": "Altíssimo contraste, retenção de prata metálica, sombras esmagadas e cores lavadas (estilo guerra/ação).",
            "contrast": 1.4,
            "saturation": 0.55,
            "gamma": 0.9,
            "grain_default": 20,
            "color_temperature": "cold_steel",
            "ffmpeg_curves": "curves=all='0/0 0.25/0.15 0.75/0.88 1/1'"
        },
        "cinema_noir": {
            "name": "Cinema Noir 35mm B&W",
            "description": "Monocromático de alto contraste, pretos profundos, granulação densa e vinheta dramática.",
            "contrast": 1.45,
            "saturation": 0.0,
            "gamma": 0.85,
            "grain_default": 25,
            "color_temperature": "monochrome",
            "ffmpeg_curves": "hue=s=0,curves=all='0/0 0.2/0.1 0.8/0.92 1/1'"
        }
    }

    @classmethod
    def get_available_film_stocks(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna lista dos perfis analógicos disponíveis."""
        return cls.FILM_STOCKS

    @classmethod
    def build_ffmpeg_film_stock_filter(cls, stock_name: str, grain_intensity: float = 1.0) -> str:
        """Gera a string de filtros FFmpeg para o perfil de filme especificado."""
        stock = cls.FILM_STOCKS.get(stock_name, cls.FILM_STOCKS["kodak_vision3_5219"])
        grain_val = int(stock["grain_default"] * grain_intensity)
        
        # Filtros: Curvas + Granulação + Vinheta se aplicável
        curves = stock["ffmpeg_curves"]
        noise_filter = f"noise=alls={grain_val}:allf=t+u" if grain_val > 0 else ""
        
        filters = [curves]
        if noise_filter:
            filters.append(noise_filter)

        return ",".join(filters)

    @classmethod
    def apply_film_stock_to_plan(cls, plan: ProjectPlan, stock_name: str, grain_intensity: float = 1.0) -> Dict[str, Any]:
        """Associa a emulação de película às configurações visuais do plano."""
        if stock_name not in cls.FILM_STOCKS:
            stock_name = "kodak_vision3_5219"

        filter_chain = cls.build_ffmpeg_film_stock_filter(stock_name, grain_intensity)
        
        setattr(plan, "color_film_stock", stock_name)
        setattr(plan, "film_stock_ffmpeg_filter", filter_chain)

        return {
            "status": "APPLIED",
            "film_stock": stock_name,
            "stock_details": cls.FILM_STOCKS[stock_name],
            "grain_intensity": grain_intensity,
            "ffmpeg_filter": filter_chain
        }
