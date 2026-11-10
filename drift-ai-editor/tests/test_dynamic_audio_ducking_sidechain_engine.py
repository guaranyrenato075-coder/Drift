import unittest
from audio.dynamic_audio_ducking_sidechain_engine import DynamicAudioDuckingSidechainEngine


class TestDynamicAudioDuckingSidechainEngine(unittest.TestCase):
    def test_calculate_ducking_filter_default(self):
        res = DynamicAudioDuckingSidechainEngine.calculate_ducking_filter()
        self.assertEqual(res["status"], "success")
        self.assertIn("sidechaincompress", res["sidechain_filter"])
        self.assertIn("amix=", res["ffmpeg_complex_filter"])

    def test_calculate_ducking_filter_custom_preset(self):
        res = DynamicAudioDuckingSidechainEngine.calculate_ducking_filter(preset="cinematic_dramatic")
        self.assertEqual(res["preset_applied"], "cinematic_dramatic")
        self.assertEqual(res["config"]["ducking_depth_db"], -20.0)

    def test_analyze_audio_track_levels(self):
        speech = [
            {"start": 1.0, "end": 6.0},
            {"start": 8.0, "end": 12.0}
        ]
        res = DynamicAudioDuckingSidechainEngine.analyze_audio_track_levels(speech, total_duration=20.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["voice_duration_sec"], 9.0)
        self.assertAlmostEqual(res["voice_coverage_pct"], 45.0)


if __name__ == "__main__":
    unittest.main()
