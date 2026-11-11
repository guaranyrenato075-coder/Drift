import unittest
from editing.lossless_audio_crossfade_integer_lut import LosslessAudioCrossfadeIntegerLUT


class TestLosslessAudioCrossfadeIntegerLUT(unittest.TestCase):
    def test_crossfade_coefficients(self):
        # Início do fade (t=0.0): out = 32767 (max), in = 0 (min)
        out_g, in_g = LosslessAudioCrossfadeIntegerLUT.get_crossfade_coefficients(0.0)
        self.assertEqual(out_g, 32767)
        self.assertEqual(in_g, 0)

        # Meio do fade (t=0.5): out e in devem ser aproximadamente 23169 (Equal Power = sqrt(2)/2 * 32767)
        out_mid, in_mid = LosslessAudioCrossfadeIntegerLUT.get_crossfade_coefficients(0.5)
        self.assertAlmostEqual(out_mid, 23169, delta=100)
        self.assertAlmostEqual(in_mid, 23169, delta=100)

        # Fim do fade (t=1.0): out = 0, in = 32767
        out_end, in_end = LosslessAudioCrossfadeIntegerLUT.get_crossfade_coefficients(1.0)
        self.assertEqual(out_end, 0)
        self.assertEqual(in_end, 32767)

    def test_benchmark_metrics(self):
        res = LosslessAudioCrossfadeIntegerLUT.benchmark_gain_lookup(total_samples=48000)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["trig_ops_eliminated_per_second"], 96000)


if __name__ == "__main__":
    unittest.main()
