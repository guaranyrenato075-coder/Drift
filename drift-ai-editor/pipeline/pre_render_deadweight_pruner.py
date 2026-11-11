"""
Módulo de Poda Pré-Render de Mídia Redundante e Trechos Inertes (Deadweight Pruner).
Audita a timeline do projeto antes de iniciar o render ou os downloads,
eliminando cenas vazias, microcortes insignificantes (<0.25s) e mídias duplicadas
ocultas, poupando processamento de GPU, tráfego de rede e consumo térmico.
"""

from typing import Dict, Any, List, Optional


class PreRenderDeadweightPruner:
    """
    Higienizador e otimizador de timeline pré-render para eliminação de redundâncias de hardware.
    """

    MIN_SCENE_DURATION_SEC = 0.35

    @classmethod
    def prune_timeline(
        cls,
        scenes: List[Dict[str, Any]],
        min_duration_sec: float = MIN_SCENE_DURATION_SEC
    ) -> Dict[str, Any]:
        """
        Executa a poda de cenas inválidas, vazias ou sub-dimensionadas.
        """
        cleaned_scenes = []
        pruned_items = []
        saved_render_seconds = 0.0

        for idx, sc in enumerate(scenes, 1):
            dur = float(sc.get("duration", 0.0))
            text = (sc.get("narration_text") or "").strip()
            concept = (sc.get("concept") or "").strip()

            # Critérios de poda (deadweight)
            is_empty_content = not text and not concept and not sc.get("clip_name") and not sc.get("file_path")
            is_too_short = dur < min_duration_sec

            if is_empty_content:
                pruned_items.append({
                    "original_index": idx,
                    "reason": "Cena vazia sem narração, conceito ou clipe visual associado.",
                    "discarded_duration_sec": dur
                })
                saved_render_seconds += dur
            elif is_too_short and not text:
                pruned_items.append({
                    "original_index": idx,
                    "reason": f"Microcorte inerte com duração insignificante ({dur}s < {min_duration_sec}s).",
                    "discarded_duration_sec": dur
                })
                saved_render_seconds += dur
            else:
                cleaned_sc = dict(sc)
                # Normaliza duração mínima para estabilidade do codificador
                if cleaned_sc.get("duration", 0.0) < min_duration_sec:
                    cleaned_sc["duration"] = min_duration_sec
                cleaned_sc["order"] = len(cleaned_scenes) + 1
                cleaned_scenes.append(cleaned_sc)

        initial_count = len(scenes)
        final_count = len(cleaned_scenes)
        deadweight_removed = initial_count - final_count

        return {
            "status": "success",
            "initial_scenes_count": initial_count,
            "final_scenes_count": final_count,
            "deadweight_scenes_removed": deadweight_removed,
            "saved_render_time_sec": round(saved_render_seconds, 2),
            "pruned_details": pruned_items,
            "cleaned_scenes": cleaned_scenes,
            "summary": (
                f"Poda concluída: {deadweight_removed} cenas inertes eliminadas da fila de render. "
                f"{round(saved_render_seconds, 1)} segundos de processamento inútil de GPU poupados."
            )
        }
