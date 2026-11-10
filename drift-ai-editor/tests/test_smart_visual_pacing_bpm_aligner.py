import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.smart_visual_pacing_bpm_aligner import SmartVisualPacingBPMAligner


class TestSmartVisualPacingBPMAligner(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Vídeo com Batida Musical",
            scenes=[
                Scene(order=1, duration=4.3),
                Scene(order=2, duration=2.1),
                Scene(order=3, duration=6.5)
            ]
        )

    def test_calculate_bpm_grid(self):
        grid = SmartVisualPacingBPMAligner.calculate_bpm_grid(bpm=120.0, time_signature=4)
        self.assertEqual(grid["quarter_note"], 0.5)      # 60 / 120 = 0.5s
        self.assertEqual(grid["full_measure"], 2.0)      # 0.5 * 4 = 2.0s

    def test_align_scenes_to_bpm(self):
        res = SmartVisualPacingBPMAligner.align_scenes_to_bpm(self.plan, bpm=120.0, alignment_mode="full_measure")
        self.assertEqual(res["status"], "ALIGNED")
        self.assertEqual(res["total_scenes_aligned"], 3)
        # Cena 1: 4.3s -> múltiplo de 2.0s mais próximo é 4.0s (2 compassos)
        self.assertEqual(self.plan.scenes[0].duration, 4.0)
        # Cena 2: 2.1s -> 2.0s (1 compasso)
        self.assertEqual(self.plan.scenes[1].duration, 2.0)
        # Cena 3: 6.5s -> 6.0s ou 8.0s (múltiplo mais próximo é 6.0s = 3 compassos)
        self.assertEqual(self.plan.scenes[2].duration, 6.0)


if __name__ == "__main__":
    unittest.main()
