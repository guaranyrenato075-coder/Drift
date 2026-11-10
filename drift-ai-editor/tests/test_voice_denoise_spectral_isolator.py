import unittest
from models.scene_plan import ProjectPlan
from audio.voice_denoise_spectral_isolator import AIVoiceDenoiseSpectralIsolator


class TestVoiceDenoiseSpectralIsolator(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(title="Projeto Áudio Ruidoso")

    def test_get_available_profiles(self):
        profiles = AIVoiceDenoiseSpectralIsolator.get_available_profiles()
        self.assertIn("studio_clean", profiles)
        self.assertIn("podcast_crisp", profiles)
        self.assertIn("broadcast_warm", profiles)
        self.assertIn("aggressive_cleanup", profiles)

    def test_build_denoise_filter_command(self):
        filt = AIVoiceDenoiseSpectralIsolator.build_denoise_filter_command("studio_clean")
        self.assertIn("afftdn=", filt)
        self.assertIn("agate=", filt)
        self.assertIn("highpass=", filt)

    def test_apply_profile_to_project(self):
        res = AIVoiceDenoiseSpectralIsolator.apply_profile_to_project(self.plan, "podcast_crisp")
        self.assertEqual(res["status"], "APPLIED")
        self.assertEqual(self.plan.voice_denoise_profile, "podcast_crisp")
        self.assertTrue(hasattr(self.plan, "voice_denoise_ffmpeg_filter"))


if __name__ == "__main__":
    unittest.main()
