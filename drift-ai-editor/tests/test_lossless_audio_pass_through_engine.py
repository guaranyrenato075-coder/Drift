import unittest
from audio.lossless_audio_pass_through_engine import LosslessAudioPassThroughEngine


class TestLosslessAudioPassThroughEngine(unittest.TestCase):
    def test_evaluate_aac_stream_compatibility(self):
        res = LosslessAudioPassThroughEngine.evaluate_audio_stream_compatibility(
            codec_name="aac",
            sample_rate=48000,
            channels=2,
            target_container="mp4"
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["can_pass_through"])
        self.assertEqual(res["ffmpeg_audio_flags"], "-c:a copy")
        self.assertEqual(res["cpu_load_reduction_pct"], 100.0)

    def test_evaluate_incompatible_codec(self):
        res = LosslessAudioPassThroughEngine.evaluate_audio_stream_compatibility(
            codec_name="vorbis",
            sample_rate=22050,
            channels=1,
            target_container="mp4"
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["can_pass_through"])
        self.assertIn("-c:a aac", res["ffmpeg_audio_flags"])


if __name__ == "__main__":
    unittest.main()
