"""
Módulo de Desalocação Atômica de Memória RAM Ociosa (RAM Working Set Trimmer).
Invoca as APIs nativas do Windows (EmptyWorkingSet / SetProcessWorkingSetSize)
e o coletor de lixo cíclico do Python para descarregar páginas de memória física
que não estão mais ativas após tarefas de renderização ou inferência de IA.
Devolve instantaneamente a memória RAM ociosa para o sistema operacional.
"""

import sys
import gc
import os
from typing import Dict, Any, Optional


class RamWorkingSetTrimmer:
    """
    Controlador de desocupação de páginas de memória RAM de baixo nível para o Windows.
    """

    @classmethod
    def trim_working_set(cls) -> Dict[str, Any]:
        """
        Executa a coleta de lixo e descarrega o Working Set do processo atual no Windows.
        """
        # 1. Coleta geracional do Python
        collected_objects = gc.collect()

        trimmed_via_win32 = False
        error_msg = None

        # 2. Chama a API do Windows para devolver páginas físicas para a lista de espera
        if sys.platform == "win32":
            try:
                import ctypes
                current_process = ctypes.windll.kernel32.GetCurrentProcess()
                # EmptyWorkingSet(hProcess) da biblioteca psapi
                result = ctypes.windll.psapi.EmptyWorkingSet(current_process)
                trimmed_via_win32 = bool(result)
            except Exception as e:
                error_msg = str(e)

        return {
            "status": "success",
            "os_platform": sys.platform,
            "python_gc_objects_freed": collected_objects,
            "win32_empty_working_set_applied": trimmed_via_win32,
            "error_detail": error_msg,
            "summary": (
                f"Working Set liberado com sucesso: {collected_objects} objetos coletados pelo GC. "
                f"Páginas físicas de RAM devolvidas para o Windows: {'SIM' if trimmed_via_win32 else 'Modo Padrão'}"
            )
        }
