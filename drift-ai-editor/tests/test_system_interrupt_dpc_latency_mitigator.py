import unittest
from core.system_interrupt_dpc_latency_mitigator import SystemInterruptDPCLatencyMitigator


class TestSystemInterruptDPCLatencyMitigator(unittest.TestCase):
    def test_optimal_and_critical_latency(self):
        # Latência baixa
        optimal = SystemInterruptDPCLatencyMitigator.evaluate_dpc_safety(measured_latency_us=250.0)
        self.assertEqual(optimal["status"], "success")
        self.assertEqual(optimal["dpc_status"], "OPTIMAL_REALTIME")

        # Latência crítica
        critical = SystemInterruptDPCLatencyMitigator.evaluate_dpc_safety(measured_latency_us=2500.0)
        self.assertEqual(critical["dpc_status"], "CRITICAL_SPIKE")
        self.assertGreater(critical["dropout_prevention_pct"], 90.0)


if __name__ == "__main__":
    unittest.main()
