import unittest
from editing.smart_selective_rerender_cache import SmartSelectiveRerenderCache


class TestSmartSelectiveRerenderCache(unittest.TestCase):
    def test_compute_scene_fingerprint(self):
        sc = {
            "duration": 5.0,
            "narration_text": "Texto da cena",
            "concept": "Conceito A",
            "clip_name": "scene1.mp4"
        }
        fp1 = SmartSelectiveRerenderCache.compute_scene_fingerprint(sc)
        fp2 = SmartSelectiveRerenderCache.compute_scene_fingerprint(sc)
        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 64)

    def test_analyze_rerender_differential(self):
        prev_scenes = [
            {"duration": 5.0, "narration_text": "Cena 1", "concept": "Conceito 1"},
            {"duration": 4.0, "narration_text": "Cena 2", "concept": "Conceito 2"}
        ]
        # Altera apenas a Cena 2
        new_scenes = [
            {"duration": 5.0, "narration_text": "Cena 1", "concept": "Conceito 1"},
            {"duration": 4.5, "narration_text": "Cena 2 modificada", "concept": "Conceito 2 alterado"}
        ]
        res = SmartSelectiveRerenderCache.analyze_rerender_differential(prev_scenes, new_scenes)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["cached_scenes_count"], 1)
        self.assertEqual(res["rerender_scenes_count"], 1)
        self.assertGreater(res["gpu_energy_saved_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
