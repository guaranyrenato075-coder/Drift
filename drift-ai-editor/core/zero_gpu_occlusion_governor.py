"""
Zero-GPU Occlusion & Window Minimize Governor for CutWire Drift AI.
Detects when the application window is minimized or occluded on Windows, throttling GUI render
framerate from 60 FPS down to 1 FPS (or complete sleep), sparing GPU cycles on entry-level GPUs (GeForce G210 972MB).
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import sys
import ctypes

@dataclass
class WindowOcclusionState:
    is_minimized: bool
    is_foreground: bool
    target_gui_fps: int
    gpu_render_active: bool
    mode_description: str

class ZeroGpuOcclusionGovernor:
    """
    Monitors Windows window state to dynamically throttle GUI frame rates.
    """

    _is_simulation_active: bool = False
    _simulated_minimized: bool = False
    _simulated_foreground: bool = True

    @classmethod
    def set_simulation_state(cls, is_minimized: bool, is_foreground: bool) -> None:
        cls._is_simulation_active = True
        cls._simulated_minimized = is_minimized
        cls._simulated_foreground = is_foreground

    @classmethod
    def clear_simulation_state(cls) -> None:
        cls._is_simulation_active = False

    @classmethod
    def get_occlusion_state(cls) -> WindowOcclusionState:
        if cls._is_simulation_active:
            is_min = cls._simulated_minimized
            is_fg = cls._simulated_foreground
        else:
            is_min = False
            is_fg = True
            if sys.platform == "win32":
                try:
                    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                    if not hwnd:
                        hwnd = ctypes.windll.user32.GetForegroundWindow()

                    if hwnd:
                        is_min = bool(ctypes.windll.user32.IsIconic(hwnd))
                        fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
                        is_fg = (hwnd == fg_hwnd)
                except Exception:
                    pass

        if is_min:
            # Janela minimizada: taxa mínima de 1 FPS (ou repouso total da GPU)
            return WindowOcclusionState(
                is_minimized=True,
                is_foreground=False,
                target_gui_fps=1,
                gpu_render_active=False,
                mode_description="Janela minimizada: GPU colocada em modo repouso (1 FPS). Consumo de VRAM zerado."
            )
        elif not is_fg:
            # Janela em segundo plano (embaixo de outra): 15 FPS
            return WindowOcclusionState(
                is_minimized=False,
                is_foreground=False,
                target_gui_fps=15,
                gpu_render_active=True,
                mode_description="Janela em segundo plano: taxa moderada (15 FPS)."
            )
        else:
            # Janela ativa e em foco: 60 FPS normal
            return WindowOcclusionState(
                is_minimized=False,
                is_foreground=True,
                target_gui_fps=60,
                gpu_render_active=True,
                mode_description="Janela em foco: renderização fluida a 60 FPS."
            )
