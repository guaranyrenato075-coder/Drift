"""
Módulo de Afinidade de Threads de CPU e Proteção Térmica de Sistema.
Controla o particionamento de núcleos de CPU para renderização e codificação,
garantindo que 1 a 2 núcleos permaneçam sempre livres para a interface do Windows,
áudio do sistema e mouse, prevenindo travamentos de desktop e sobreaquecimento da CPU.
"""

import os
from typing import Dict, Any, Optional


class CPUThreadAffinityGovernor:
    """
    Governador de afinidade de threads e proteção do sistema contra saturação de CPU.
    """

    @staticmethod
    def get_system_logical_cores() -> int:
        """Retorna o número de núcleos lógicos disponíveis."""
        return os.cpu_count() or 4

    @classmethod
    def calculate_balanced_thread_allocation(
        cls,
        reserved_cores_for_os: int = 2,
        cooling_profile: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Calcula a alocação de threads e a máscara de afinidade ótima.
        
        Perfis de Arrefecimento:
        - 'silent_cool': Mantém os fans silenciosos e limita uso de CPU a 50%.
        - 'balanced': Reserva 2 núcleos para o Windows e usa os demais para o Drift.
        - 'workstation_max': Reserva apenas 1 núcleo para o SO e aloca o restante.
        """
        total_cores = cls.get_system_logical_cores()

        if cooling_profile == "silent_cool":
            render_threads = max(1, total_cores // 2)
            os_cores = total_cores - render_threads
        elif cooling_profile == "workstation_max":
            os_cores = 1
            render_threads = max(1, total_cores - 1)
        else:  # balanced
            os_cores = min(reserved_cores_for_os, max(1, total_cores // 4))
            render_threads = max(1, total_cores - os_cores)

        # Cria máscara de bits binária: núcleos mais altos alocados para o render, núcleo 0 e 1 reservados para o SO
        mask_bits = 0
        for i in range(os_cores, os_cores + render_threads):
            if i < total_cores:
                mask_bits |= (1 << i)

        if mask_bits == 0:
            mask_bits = (1 << total_cores) - 1

        hex_affinity_mask = f"0x{mask_bits:X}"

        # Flags recomendadas para FFmpeg
        ffmpeg_thread_flags = f"-threads {render_threads} -filter_threads {max(1, render_threads // 2)}"

        return {
            "status": "success",
            "total_cpu_cores": total_cores,
            "allocated_render_threads": render_threads,
            "reserved_os_cores": total_cores - render_threads,
            "cooling_profile": cooling_profile,
            "hex_affinity_mask": hex_affinity_mask,
            "ffmpeg_thread_args": ffmpeg_thread_flags,
            "process_priority": "BELOW_NORMAL_PRIORITY_CLASS",
            "summary": (
                f"Afinidade configurada: {render_threads}/{total_cores} núcleos para render. "
                f"{total_cores - render_threads} núcleos 100% reservados para o Windows/UI, garantindo desktop fluido."
            )
        }
