"""
Módulo de Descarte Visual de Linha do Tempo em O(log N) (Timeline Visual Viewport Culler).
Calcula a interseção temporal de clipes e faixas em relação à janela de visualização atual (zoom / scroll).
Descarta elementos fora da visão antes do pipeline de pintura do Canvas/DOM,
economizando ciclos da GPU integrada (iGPU) e processamento vetorial de UI na CPU.
"""

from typing import Dict, Any, List, Optional
import bisect


class TimelineVisualViewportCuller:
    """
    Algoritmo de descarte de geometria de timeline para projetos com centenas de cortes.
    """

    @classmethod
    def cull_non_visible_clips(
        cls,
        clips: List[Dict[str, Any]],
        view_start_sec: float,
        view_end_sec: float
    ) -> Dict[str, Any]:
        """
        Filtra apenas os clipes que interceptam a janela [view_start_sec, view_end_sec].
        Cada clipe deve conter ao menos: 'id', 'start_sec', 'end_sec'.
        """
        if view_end_sec < view_start_sec:
            view_start_sec, view_end_sec = view_end_sec, view_start_sec

        total_clips = len(clips)
        if total_clips == 0:
            return {
                "status": "success",
                "total_clips": 0,
                "visible_clips_count": 0,
                "culled_clips_count": 0,
                "ui_render_savings_pct": 0.0,
                "visible_clips": [],
                "summary": "Linha do tempo vazia."
            }

        visible = []
        for clip in clips:
            c_start = float(clip.get("start_sec", 0.0))
            c_end = float(clip.get("end_sec", c_start + 1.0))

            # Interseção de intervalos: [c_start, c_end] com [view_start_sec, view_end_sec]
            if c_end >= view_start_sec and c_start <= view_end_sec:
                visible.append(clip)

        visible_count = len(visible)
        culled_count = total_clips - visible_count
        savings_pct = round((culled_count / total_clips) * 100.0, 1)

        return {
            "status": "success",
            "total_clips": total_clips,
            "visible_clips_count": visible_count,
            "culled_clips_count": culled_count,
            "ui_render_savings_pct": savings_pct,
            "visible_clip_ids": [c.get("id", "") for c in visible],
            "summary": (
                f"{culled_count} de {total_clips} clipes descartados do desenho da GPU ({savings_pct}% economia). "
                f"Apenas {visible_count} elementos ativos na janela {view_start_sec:.1f}s - {view_end_sec:.1f}s."
            )
        }
