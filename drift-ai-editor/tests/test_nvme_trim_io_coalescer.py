import unittest
from core.nvme_trim_io_coalescer import NVMeTrimIOCoalescer


class TestNVMeTrimIOCoalescer(unittest.TestCase):
    def test_unaligned_buffer_padded_to_4k(self):
        res = NVMeTrimIOCoalescer.calculate_coalesced_buffer_size(5000)
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_4k_aligned"])
        self.assertEqual(res["aligned_output_bytes"], 8192)  # 2 setores de 4096
        self.assertEqual(res["padding_bytes"], 3192)
        self.assertEqual(res["sectors_4k_count"], 2)

    def test_already_aligned_buffer(self):
        res = NVMeTrimIOCoalescer.calculate_coalesced_buffer_size(4096)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_4k_aligned"])
        self.assertEqual(res["padding_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
