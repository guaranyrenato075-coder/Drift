import unittest
from audio.soundfx_doppler_pan_automator import SoundFXDopplerPanAutomator


class TestSoundFXDopplerPanAutomator(unittest.TestCase):
    def test_calculate_doppler_envelope(self):
        res = SoundFXDopplerPanAutomator.calculate_doppler_envelope(
            duration=3.0,
            approach_speed_kmh=150.0,
            direction="left_to_right"
        )
        self.assertEqual(res["duration"], 3.0)
        self.assertGreater(res["approach_pitch_ratio"], 1.0)
        self.assertLess(res["recede_pitch_ratio"], 1.0)
        self.assertEqual(res["start_pan"], -1.0)
        self.assertEqual(res["end_pan"], 1.0)
        self.assertIn("asetrate=", res["ffmpeg_filter"])
        self.assertIn("pan=stereo", res["ffmpeg_filter"])


if __name__ == "__main__":
    unittest.main()
