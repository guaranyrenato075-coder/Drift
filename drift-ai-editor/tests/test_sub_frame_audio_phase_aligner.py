import unittest
from editing.sub_frame_audio_phase_aligner import SubFrameAudioPhaseAligner


class TestSubFrameAudioPhaseAligner(unittest.TestCase):
    def test_zero_crossing_snap(self):
        # Onda senoidal aproximada: amostra com corte em pico (20000), descendo para 0 na posição +3
        samples = [15000, 20000, 12000, 500, 0, -500, -8000]
        # Corte nominal no índice 1 (onde amplitude é 20000)
        res = SubFrameAudioPhaseAligner.snap_to_zero_crossing(samples, nominal_cut_index=1, search_window=4)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["adjusted_cut_index"], 4)  # Onde amplitude é 0
        self.assertEqual(res["snapped_zero_amplitude"], 0)
        self.assertTrue(res["acoustic_transient_suppressed"])


if __name__ == "__main__":
    unittest.main()
