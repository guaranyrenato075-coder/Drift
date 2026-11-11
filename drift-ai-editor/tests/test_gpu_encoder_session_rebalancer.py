import unittest
from pipeline.gpu_encoder_session_rebalancer import GPUEncoderSessionRebalancer


class TestGPUEncoderSessionRebalancer(unittest.TestCase):
    def test_session_admission_and_rejection(self):
        # 1 sessão ativa: aprova normalmente
        res1 = GPUEncoderSessionRebalancer.evaluate_session_admission(active_sessions_count=1, max_allowed_sessions=3)
        self.assertEqual(res1["status"], "success")
        self.assertTrue(res1["can_admit_hardware"])
        self.assertEqual(res1["allocation_mode"], "HARDWARE_ASIC_APPROVED")

        # 3 sessões ativas: atinge teto, enfileira
        res3 = GPUEncoderSessionRebalancer.evaluate_session_admission(active_sessions_count=3, max_allowed_sessions=3)
        self.assertFalse(res3["can_admit_hardware"])
        self.assertEqual(res3["allocation_mode"], "QUEUED_HYBRID_PACE")


if __name__ == "__main__":
    unittest.main()
