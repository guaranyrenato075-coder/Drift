"""
Unit tests for AutoThumbnailVisualComposer in Drift AI.
Verifies thumbnail composition, hero media selection, resolution standards, and headline branding.
"""
import unittest
import tempfile
from pathlib import Path
from pipeline.thumbnail_composer import AutoThumbnailVisualComposer, ThumbnailCompositionResult
from models.scene_plan import ProjectPlan, Scene, MediaCandidate

class TestThumbnailComposer(unittest.TestCase):

    def test_compose_thumbnail(self):
        plan = ProjectPlan(title="Projeto Mistérios do Cosmos")
        cand = MediaCandidate(candidate_id="c_nasa", platform="nasa", copyright_risk="safe")
        s = Scene(order=1, narration_text="As nebulosas no espaço profundo.")
        s.selected_media = cand
        plan.scenes = [s]

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_img = Path(tmp_dir) / "thumb_test.png"
            result = AutoThumbnailVisualComposer.compose_thumbnail(plan, headline_text="O SEGREDO", output_path=str(out_img))

            self.assertIsInstance(result, ThumbnailCompositionResult)
            self.assertTrue(out_img.exists())
            self.assertEqual(result.width, 1280)
            self.assertEqual(result.height, 720)
            self.assertEqual(result.hero_platform, "nasa")
            self.assertEqual(result.headline_text, "O SEGREDO")

if __name__ == "__main__":
    unittest.main()
