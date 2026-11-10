"""
Unit tests for SmartAudioDenoiseEnhancer in Drift AI.
Verifies audio profile listing, EBU R128 loudness normalization and FFmpeg filter building.
"""
import unittest
from audio.smart_audio_denoise_enhancer import SmartAudioDenoiseEnhancer

class TestSmartAudioDenoiseEnhancer(unittest.TestCase):

    def test_list_profiles(self):
        profiles = SmartAudioDenoiseEnhancer.list_profiles()
        self.assertGreaterEqual(len(profiles), 4)
        p_ids = {p["id"] for p in profiles}
        self.assertIn("broadcast_lufs_14", p_ids)
        self.assertIn("radio_podcast_warmth", p_ids)
        self.assertIn("crisp_clarity", p_ids)

    def test_get_filter_for_broadcast(self):
        filter_str = SmartAudioDenoiseEnhancer.get_filter_for_profile("broadcast_lufs_14")
        self.assertIn("loudnorm=I=-14", filter_str)
        self.assertIn("highpass=f=80", filter_str)

    def test_build_loudnorm_filter_string(self):
        custom = SmartAudioDenoiseEnhancer.build_loudnorm_filter_string(target_lufs=-16.0, lra=8.0)
        self.assertEqual(custom, "loudnorm=I=-16.0:LRA=8.0:tp=-1.5")

if __name__ == "__main__":
    unittest.main()
