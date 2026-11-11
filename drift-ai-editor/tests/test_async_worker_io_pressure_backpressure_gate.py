import unittest
from pipeline.async_worker_io_pressure_backpressure_gate import AsyncWorkerIOPressureBackpressureGate


class TestAsyncWorkerIOPressureBackpressureGate(unittest.TestCase):
    def test_clear_and_throttled_states(self):
        # Fila limpa
        clear_res = AsyncWorkerIOPressureBackpressureGate.evaluate_queue_backpressure(current_pending_tasks=5)
        self.assertEqual(clear_res["status"], "success")
        self.assertEqual(clear_res["gate_state"], "CLEAR")
        self.assertFalse(clear_res["backpressure_active"])

        # Fila sobrecarregada
        throttled_res = AsyncWorkerIOPressureBackpressureGate.evaluate_queue_backpressure(current_pending_tasks=40)
        self.assertEqual(throttled_res["gate_state"], "THROTTLED")
        self.assertTrue(throttled_res["backpressure_active"])
        self.assertGreater(throttled_res["recommended_hold_delay_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
