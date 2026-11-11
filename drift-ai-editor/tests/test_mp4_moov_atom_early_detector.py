import unittest
from media.mp4_moov_atom_early_detector import MP4MoovAtomEarlyDetector


class TestMP4MoovAtomEarlyDetector(unittest.TestCase):
    def test_faststart_moov_header(self):
        header = b"\x00\x00\x00\x20ftypmp42\x00\x00\x01\x00moov\x00\x00\x00lmvhd"
        res = MP4MoovAtomEarlyDetector.analyze_moov_placement(
            file_size_bytes=100 * 1024 * 1024,  # 100 MB
            header_bytes=header
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_faststart"])
        self.assertEqual(res["moov_location"], "HEAD")
        self.assertGreater(res["ssd_read_reduction_pct"], 99.0)

    def test_tail_moov_seek(self):
        header = b"\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mdat..."
        res = MP4MoovAtomEarlyDetector.analyze_moov_placement(
            file_size_bytes=1024 * 1024 * 1024,  # 1 GB
            header_bytes=header,
            footer_bytes=b"\x00\x00\x01\x00moov..."
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_faststart"])
        self.assertEqual(res["moov_location"], "TAIL_SEEK")
        self.assertGreater(res["ssd_read_reduction_pct"], 99.0)


if __name__ == "__main__":
    unittest.main()
