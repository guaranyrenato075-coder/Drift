import unittest
from media.audio_resample_subsampling_bypass import AudioResampleSubsamplingBypass


class TestAudioResampleSubsamplingBypass(unittest.TestCase):
    def test_direct_bypass(self):
        res = AudioResampleSubsamplingBypass.evaluate_audio_filter_chain(
            source_sample_rate_hz=48000,
            target_sample_rate_hz=48000,
            source_channels=2,
            target_channels=2
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["can_bypass_resample"])
        self.assertEqual(res["ffmpeg_audio_filter"], "anull")
        self.assertEqual(res["cpu_audio_processing_savings_pct"], 100.0)

    def test_active_resample(self):
        res = AudioResampleSubsamplingBypass.evaluate_audio_filter_chain(
            source_sample_rate_hz=44100,
            target_sample_rate_hz=48000,
            source_channels=2,
            target_channels=2
        )
        self.assertFalse(res["can_bypass_resample"])
        self.assertIn("aresample", res["ffmpeg_audio_filter"])


if __name__ == "__main__":
    unittest.main()
