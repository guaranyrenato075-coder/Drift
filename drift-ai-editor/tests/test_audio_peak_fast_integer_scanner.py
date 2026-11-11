import unittest
from editing.audio_peak_fast_integer_scanner import AudioPeakFastIntegerScanner


class TestAudioPeakFastIntegerScanner(unittest.TestCase):
    def test_scan_silent_bytes(self):
        res = AudioPeakFastIntegerScanner.scan_pcm16_samples(b"\x00\x00" * 100)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["samples_count"], 100)
        self.assertEqual(res["peak_integer"], 0)
        self.assertFalse(res["has_clipping"])

    def test_scan_loud_samples_with_clipping(self):
        # 32767 little endian: \xff\x7f
        loud_bytes = (b"\xff\x7f") * 10
        res = AudioPeakFastIntegerScanner.scan_pcm16_samples(loud_bytes)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["peak_integer"], 32767)
        self.assertTrue(res["has_clipping"])
        self.assertEqual(res["peak_dbfs"], 0.0)


if __name__ == "__main__":
    unittest.main()
