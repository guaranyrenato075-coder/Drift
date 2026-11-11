"""
Módulo de Pacer Adaptativo de Arrefecimento Térmico (Thermal Adaptive Render Pacer).
Monitora os ciclos de processamento contínuo de renderização e introduz pausas
microscópicas estratégicas de arrefecimento entre lotes de cenas pesadas.
Permite que os dissipadores de calor e ventoinhas estabilizem a temperatura dos
chips de CPU e GPU, prevenindo thermal throttling e desgaste dos circuitos.
"""

from typing import Dict, Any, Optional


class ThermalAdaptiveRenderPacer:
    """
    Controlador de duty-cycle térmico preventivo para sessões de render prolongadas.
    """

    COOLING_PROFILES = {
        "silent_eco": {
            "name": "Silencioso & Frio (<65°C)",
            "max_continuous_work_sec": 30.0,
            "cool_down_pause_ms": 400,
            "fan_noise_level": "Baixo / Silencioso",
            "target_cpu_temp_c": 60.0
        },
        "balanced": {
            "name": "Equilibrado Padrão (65°C - 75°C)",
            "max_continuous_work_sec": 60.0,
            "cool_down_pause_ms": 250,
            "fan_noise_level": "Moderado",
            "target_cpu_temp_c": 70.0
        },
        "turbo_workstation": {
            "name": "Render Acelerado / Alta Ventilação",
            "max_continuous_work_sec": 120.0,
            "cool_down_pause_ms": 100,
            "fan_noise_level": "Alto",
            "target_cpu_temp_c": 80.0
        }
    }

    @classmethod
    def calculate_inter_scene_pause(
        cls,
        elapsed_work_seconds: float,
        profile: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Calcula a pausa de arrefecimento necessária com base no tempo de carga decorrido.
        """
        cfg = cls.COOLING_PROFILES.get(profile, cls.COOLING_PROFILES["balanced"])
        max_work = cfg["max_continuous_work_sec"]
        base_pause = cfg["cool_down_pause_ms"]

        # Se ultrapassou o teto de trabalho contínuo, aplica pausa de alívio térmico
        if elapsed_work_seconds >= max_work:
            required_pause_ms = base_pause
            needs_cool_down = True
            advice = f"Pausa preventiva de {required_pause_ms}ms inserida para estabilização térmica do dissipador."
        else:
            required_pause_ms = 0
            needs_cool_down = False
            advice = "Temperatura estável. Sem necessidade de pausa térmica neste ciclo."

        return {
            "status": "success",
            "profile": profile,
            "profile_name": cfg["name"],
            "elapsed_continuous_work_sec": round(elapsed_work_seconds, 2),
            "max_continuous_work_sec": max_work,
            "needs_cool_down": needs_cool_down,
            "pause_ms": required_pause_ms,
            "fan_noise_estimate": cfg["fan_noise_level"],
            "target_max_temp_c": cfg["target_cpu_temp_c"],
            "advice": advice
        }
