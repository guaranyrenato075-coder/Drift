"""
Automated Sound FX & Foley Cue Generator for CutWire Drift AI.
Analyzes scene narrations, timings, and visual descriptions to identify cinematic foley cues
(whooshes, clock ticks, ambient wind, camera clicks, page turns, cinematic impacts) and prepares
synchronized micro-audio tracks with gentle ducking.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re
from models.scene_plan import Scene, ProjectPlan

@dataclass
class FoleyCue:
    cue_id: str
    scene_order: int
    category: str
    label: str
    trigger_keyword: str
    relative_start_sec: float
    duration_sec: float
    suggested_volume_db: float
    auto_ducking: bool = False

class SoundFXAutoFoley:
    """
    Context-aware audio foley and sound effects orchestrator.
    """

    FOLEY_PATTERNS: Dict[str, Dict[str, Any]] = {
        "wind_atmosphere": {
            "keywords": ["vento", "wind", "sopra", "deserto", "tempestade", "frio", "vazio", "ar", "montanha", "breeze"],
            "label": "Vento & Atmosfera Desolada",
            "duration": 4.0,
            "volume_db": -22.0,
            "ducking": False
        },
        "clock_tick": {
            "keywords": ["tempo", "time", "segundos", "minutos", "horas", "urgente", "deadline", "relógio", "clock", "espera"],
            "label": "Tique-taque de Relógio Sutil",
            "duration": 2.5,
            "volume_db": -18.0,
            "ducking": False
        },
        "camera_shutter": {
            "keywords": ["foto", "câmera", "fotografia", "retrato", "capturou", "flash", "imagem", "registro"],
            "label": "Clique de Obturador Fotográfico",
            "duration": 0.8,
            "volume_db": -14.0,
            "ducking": True
        },
        "page_turn": {
            "keywords": ["livro", "página", "manuscrito", "história", "escrito", "diário", "documento", "lendo", "ler"],
            "label": "Virar de Página de Papel Antigo",
            "duration": 1.2,
            "volume_db": -16.0,
            "ducking": False
        },
        "thunder_rumble": {
            "keywords": ["trovão", "raio", "tempestade", "chover", "chuva", "trovoada", "dark", "storm"],
            "label": "Ressonância Distante de Trovão",
            "duration": 3.5,
            "volume_db": -16.0,
            "ducking": True
        },
        "cinematic_impact": {
            "keywords": ["impacto", "colisão", "explosão", "choque", "destruição", "surpresa", "inesperado", "poderoso"],
            "label": "Impacto / Sub-Drop Cinematográfico Suave",
            "duration": 2.0,
            "volume_db": -12.0,
            "ducking": True
        },
        "cosmic_drone": {
            "keywords": ["universo", "cosmos", "estrela", "galáxia", "buraco negro", "espaço", "infinito", "astro"],
            "label": "Drone Cósmico Profundo (Espaço)",
            "duration": 4.5,
            "volume_db": -24.0,
            "ducking": False
        }
    }

    @classmethod
    def analyze_scene_foley(cls, scene: Scene) -> List[FoleyCue]:
        """
        Scans a scene narration and keywords for foley opportunities.
        """
        cues: List[FoleyCue] = []
        combined_text = (scene.narration_text + " " + scene.visual_description + " " + " ".join(scene.english_keywords or [])).lower()
        words = set(re.findall(r'[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ0-9_-]+', combined_text))

        scene_dur = max(scene.duration or 3.0, 1.0)
        cue_idx = 1

        for category, config in cls.FOLEY_PATTERNS.items():
            matched_kw = [k for k in config["keywords"] if k.lower() in words]
            if matched_kw:
                # Distribute within the scene timeline
                start_sec = round(min(0.5 * cue_idx, max(0.0, scene_dur - config["duration"])), 2)
                cue = FoleyCue(
                    cue_id=f"foley_s{scene.order}_{cue_idx}",
                    scene_order=scene.order,
                    category=category,
                    label=config["label"],
                    trigger_keyword=matched_kw[0],
                    relative_start_sec=start_sec,
                    duration_sec=min(config["duration"], scene_dur),
                    suggested_volume_db=config["volume_db"],
                    auto_ducking=config["ducking"]
                )
                cues.append(cue)
                cue_idx += 1
                if len(cues) >= 2:  # Max 2 subtle foley cues per scene to keep audio clean
                    break

        return cues

    @classmethod
    def generate_plan_foley_manifest(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """
        Generates full foley map for the entire project.
        """
        manifest = []
        total_cues = 0
        for s in plan.scenes:
            scene_cues = cls.analyze_scene_foley(s)
            total_cues += len(scene_cues)
            for c in scene_cues:
                manifest.append({
                    "cue_id": c.cue_id,
                    "scene_order": c.scene_order,
                    "category": c.category,
                    "label": c.label,
                    "trigger_keyword": c.trigger_keyword,
                    "relative_start_sec": c.relative_start_sec,
                    "duration_sec": c.duration_sec,
                    "suggested_volume_db": c.suggested_volume_db,
                    "auto_ducking": c.auto_ducking
                })

        return {
            "project_id": plan.project_id,
            "total_scenes": len(plan.scenes),
            "total_foley_cues": total_cues,
            "cues": manifest
        }
