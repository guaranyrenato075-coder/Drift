import unittest
from editing.avx_downclocking_frequency_guard import AVXDownclockingFrequencyGuard


class TestAVXDownclockingFrequencyGuard(unittest.TestCase):
    def test_avx2_chunk_sizing(self):
        res = AVXDownclockingFrequencyGuard.calculate_simd_chunk_size(
            total_elements=50000,
            simd_instruction_set="avx2"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["optimal_chunk_size"], 4096)
        self.assertGreater(res["turbo_clock_penalty_prevented_mhz"], 0.0)

    def test_avx512_safety_chunk(self):
        res = AVXDownclockingFrequencyGuard.calculate_simd_chunk_size(
            total_elements=50000,
            simd_instruction_set="avx512"
        )
        self.assertEqual(res["optimal_chunk_size"], 2048)


if __name__ == "__main__":
    unittest.main()
