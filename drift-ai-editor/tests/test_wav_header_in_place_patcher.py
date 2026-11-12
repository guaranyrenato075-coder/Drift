import unittest
import tempfile
import os
from media.wav_header_in_place_patcher import WAVHeaderInPlacePatcher


class TestWAVHeaderInPlacePatcher(unittest.TestCase):
    def test_patch_wav_header(self):
        # Cria um arquivo mock de 44 bytes de cabeçalho WAV
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00")
            temp_path = tf.name

        try:
            res = WAVHeaderInPlacePatcher.patch_wav_header(temp_path, total_data_bytes=44100 * 4)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["patched_bytes"], 8)
            self.assertEqual(res["updated_data_size"], 176400)
            self.assertEqual(res["updated_riff_size"], 176400 + 36)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_simulate_ssd_write_reduction(self):
        sim = WAVHeaderInPlacePatcher.simulate_ssd_write_reduction(audio_duration_sec=60.0)
        self.assertEqual(sim["status"], "success")
        self.assertEqual(sim["physical_ssd_bytes_written"], 8)
        self.assertGreater(sim["ssd_write_reduction_pct"], 99.0)


if __name__ == "__main__":
    unittest.main()
