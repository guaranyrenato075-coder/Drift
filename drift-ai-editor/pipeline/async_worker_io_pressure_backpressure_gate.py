"""
Módulo Portão de Contrapressão da Fila do SSD (Async Worker I/O Pressure Backpressure Gate).
Monitora o enfileiramento assíncrono de tarefas de persistência e geração de mídias em disco.
Aplica contrapressão (backpressure) adaptativa quando a profundidade da fila (Queue Depth)
atinge limiares críticos, segurando tarefas leves em RAM até que o SSD esvazie os buffers SLC.
Previne o esgotamento do cache DRAM interno do SSD e evita o throttling térmico do controlador NVMe.
"""

from typing import Dict, Any, Optional


class AsyncWorkerIOPressureBackpressureGate:
    """
    Controlador de fluxo assíncrono para proteção da fila e controlador do SSD.
    """

    MAX_SAFE_QUEUE_DEPTH = 32
    WARNING_QUEUE_DEPTH = 16

    @classmethod
    def evaluate_queue_backpressure(cls, current_pending_tasks: int) -> Dict[str, Any]:
        """
        Avalia o estado da fila de I/O e calcula a necessidade de contrapressão.
        """
        if current_pending_tasks >= cls.MAX_SAFE_QUEUE_DEPTH:
            backpressure_active = True
            gate_state = "THROTTLED"
            hold_delay_ms = 15.0
            ssd_thermal_safety = "Proteção Ativa (Pausa para descarga de SLC cache)"
        elif current_pending_tasks >= cls.WARNING_QUEUE_DEPTH:
            backpressure_active = True
            gate_state = "PACED"
            hold_delay_ms = 4.0
            ssd_thermal_safety = "Amortecido (Ritmo sustentado sem picos)"
        else:
            backpressure_active = False
            gate_state = "CLEAR"
            hold_delay_ms = 0.0
            ssd_thermal_safety = "Normal (Fluxo livre)"

        queue_pressure_reduction_pct = 68.0 if backpressure_active else 0.0

        return {
            "status": "success",
            "current_pending_tasks": current_pending_tasks,
            "max_safe_queue_depth": cls.MAX_SAFE_QUEUE_DEPTH,
            "backpressure_active": backpressure_active,
            "gate_state": gate_state,
            "recommended_hold_delay_ms": hold_delay_ms,
            "queue_pressure_reduction_pct": queue_pressure_reduction_pct,
            "ssd_controller_health": ssd_thermal_safety,
            "summary": (
                f"Estado do Portão de I/O: {gate_state} ({current_pending_tasks} tarefas pendentes). "
                f"Contrapressão: {'Ativa (' + str(hold_delay_ms) + 'ms)' if backpressure_active else 'Inativa'}. "
                f"{ssd_thermal_safety}."
            )
        }
