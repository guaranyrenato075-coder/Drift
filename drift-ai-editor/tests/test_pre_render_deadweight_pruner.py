import unittest
from pipeline.pre_render_deadweight_pruner import PreRenderDeadweightPruner


class TestPreRenderDeadweightPruner(unittest.TestCase):
    def test_prune_timeline_empty_scenes(self):
        scenes = [
            {"duration": 4.0, "narration_text": "Cena válida", "concept": "Intro"},
            {"duration": 2.0, "narration_text": "", "concept": "", "clip_name": "", "file_path": ""},  # Vazia
            {"duration": 0.1, "narration_text": "", "concept": "Microcorte"},  # Curta demais sem narração
            {"duration": 3.0, "narration_text": "Cena final", "concept": "Fim"}
        ]
        res = PreRenderDeadweightPruner.prune_timeline(scenes, min_duration_sec=0.35)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["initial_scenes_count"], 4)
        self.assertEqual(res["final_scenes_count"], 2)
        self.assertEqual(res["deadweight_scenes_removed"], 2)
        self.assertGreater(res["saved_render_time_sec"], 0.0)


if __name__ == "__main__":
    unittest.main()
