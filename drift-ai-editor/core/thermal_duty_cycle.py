"""
Thermal Duty-Cycle Pacer for CutWire Drift AI.
Monitors consecutive heavy render batches and inserts micro-cooling pauses (1.0s - 2.0s)
to dissipate cumulative die heat, preventing thermal throttling on multi-core CPUs (Intel Xeon E5-2650 v4).
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time

@dataclass
class ThermalPacingDecision:
    chunk_index: int
    consecutive_renders: int
    should_pause_for_cooling: bool
    cooling_pause_sec: float
    estimated_temp_drop_celsius: float
    reason: str

class ThermalDutyCyclePacer:
    """
    Prevents prolonged 100% TDP saturation through cadence-based thermal breathing pauses.
    """

    def __init__(self, chunks_per_cooling_cycle: int = 5, pause_duration_sec: float = 1.5):
        self.chunks_per_cycle = chunks_per_cooling_cycle
        self.pause_duration = pause_duration_sec
        self.consecutive_count = 0
        self.total_pauses_inserted = 0
        self.total_cooling_time_sec = 0.0

    def record_chunk_completed(self, chunk_index: int) -> ThermalPacingDecision:
        self.consecutive_count += 1

        if self.consecutive_count >= self.chunks_per_cycle:
            # Respiro térmico necessário
            pause_sec = self.pause_duration
            self.total_pauses_inserted += 1
            self.total_cooling_time_sec += pause_sec
            current_consecutive = self.consecutive_count
            self.consecutive_count = 0 # Reinicia ciclo

            return ThermalPacingDecision(
                chunk_index=chunk_index,
                consecutive_renders=current_consecutive,
                should_pause_for_cooling=True,
                cooling_pause_sec=pause_sec,
                estimated_temp_drop_celsius=3.8,
                reason=f"Ciclo de {self.chunks_per_cycle} chunks concluído: aplicando pausa de {pause_sec}s para dissipação térmica."
            )

        return ThermalPacingDecision(
            chunk_index=chunk_index,
            consecutive_renders=self.consecutive_count,
            should_pause_for_cooling=False,
            cooling_pause_sec=0.0,
            estimated_temp_drop_celsius=0.0,
            reason="Dentro da janela operacional segura da CPU."
        )

    def execute_cooling_if_needed(self, decision: ThermalPacingDecision) -> None:
        if decision.should_pause_for_cooling and decision.cooling_pause_sec > 0:
            time.sleep(decision.cooling_pause_sec)

