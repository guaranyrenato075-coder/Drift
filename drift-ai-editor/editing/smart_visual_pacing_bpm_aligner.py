"""
Smart Visual Pacing & BPM Aligner.
Alinha milimetricamente os pontos de corte de cenas às batidas da trilha sonora (BPM Grid),
criando sincronização rítmica hipnótica entre imagem e música.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class SmartVisualPacingBPMAligner:
    """Ajusta as durações das cenas para quantização precisa na grade de BPM."""

    @classmethod
    def calculate_bpm_grid(cls, bpm: float = 120.0, time_signature: int = 4) -> Dict[str, float]:
        """Calcula os intervalos em segundos para tempos e compassos."""
        seconds_per_beat = 60.0 / max(bpm, 20.0)
        seconds_per_measure = seconds_per_beat * time_signature
        return {
            "quarter_note": round(seconds_per_beat, 3),         # Semínima (1 tempo)
            "eighth_note": round(seconds_per_beat / 2.0, 3),    # Colcheia (1/2 tempo)
            "full_measure": round(seconds_per_measure, 3),      # Compasso inteiro
            "two_measures": round(seconds_per_measure * 2.0, 3) # Dois compassos
        }

    @classmethod
    def align_scenes_to_bpm(
        cls,
        plan: ProjectPlan,
        bpm: float = 120.0,
        alignment_mode: str = "full_measure"
    ) -> Dict[str, Any]:
        """Recalcula as durações das cenas aproximando-as do múltiplo musical mais próximo."""
        grid = cls.calculate_bpm_grid(bpm)
        grid_step = grid.get(alignment_mode, grid["full_measure"])

        scenes = getattr(plan, "scenes", [])
        adjustments = []
        accumulated_original = 0.0
        accumulated_aligned = 0.0

        for idx, scene in enumerate(scenes):
            orig_duration = float(getattr(scene, "duration", 5.0))
            # Quantiza para o múltiplo mais próximo do grid_step (mínimo 1 step)
            steps_count = max(1, round(orig_duration / grid_step))
            aligned_duration = round(steps_count * grid_step, 3)

            diff = round(aligned_duration - orig_duration, 3)
            accumulated_original += orig_duration
            accumulated_aligned += aligned_duration

            # Aplica nova duração à cena
            scene.duration = aligned_duration

            adjustments.append({
                "scene_index": idx + 1,
                "original_duration": orig_duration,
                "aligned_duration": aligned_duration,
                "delta": diff,
                "measure_units": steps_count
            })

        return {
            "bpm": bpm,
            "alignment_mode": alignment_mode,
            "grid_interval_seconds": grid_step,
            "total_scenes_aligned": len(scenes),
            "original_total_duration": round(accumulated_original, 2),
            "aligned_total_duration": round(accumulated_aligned, 2),
            "adjustments": adjustments,
            "status": "ALIGNED"
        }
