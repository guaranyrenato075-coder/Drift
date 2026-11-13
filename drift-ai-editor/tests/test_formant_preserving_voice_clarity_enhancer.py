import unittest
from audio.formant_preserving_voice_clarity_enhancer import FormantPreservingVoiceClarityEnhancer


class TestFormantPreservingVoiceClarityEnhancer(unittest.TestCase):
    def test_calculate_spectral_carving_profile(self):
        # Fala ativa
        active = FormantPreservingVoiceClarityEnhancer.calculate_spectral_carving_profile(is_speech_present=True)
        self.assertEqual(active["status"], "success")
        self.assertTrue(active["speech_active"])
        self.assertEqual(active["music_notch_attenuation_db"], -4.5)
        self.assertGreater(active["speech_intelligibility_boost_pct"], 30.0)

        # Fala inativa
        inactive = FormantPreservingVoiceClarityEnhancer.calculate_spectral_carving_profile(is_speech_present=False)
        self.assertFalse(inactive["speech_active"])
        self.assertEqual(inactive["music_notch_attenuation_db"], 0.0)

    def test_benchmark_clarity_efficiency(self):
        bench = FormantPreservingVoiceClarityEnhancer.benchmark_clarity_efficiency()
        self.assertEqual(bench["status"], "success")
        self.assertLess(bench["cpu_overhead_pct"], 2.0)


if __name__ == "__main__":
    unittest.main()
