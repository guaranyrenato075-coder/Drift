"""
Unit tests for SoundFXAutoFoley in Drift AI.
Verifies keyword-driven foley cue detection and audio manifest generation.
"""
import unittest
from audio.sound_fx_foley import SoundFXAutoFoley, FoleyCue
from models.scene_plan import ProjectPlan, Scene

class TestSoundFXAutoFoley(unittest.TestCase):

    def test_analyze_scene_foley_detection(self):
        scene = Scene(
            order=1,
            narration_text="O vento sopra gélido pelas montanhas enquanto ouvimos o trovão distante.",
            visual_description="Cold mountain peaks under storm clouds.",
            english_keywords=["mountain", "storm"],
            duration=5.0
        )
        cues = SoundFXAutoFoley.analyze_scene_foley(scene)
        self.assertGreaterEqual(len(cues), 1)
        categories = [c.category for c in cues]
        self.assertTrue(any(cat in categories for cat in ["wind_atmosphere", "thunder_rumble"]))

    def test_generate_plan_foley_manifest(self):
        plan = ProjectPlan(title="História dos Manuscritos")
        plan.scenes = [
            Scene(order=1, narration_text="Abrindo o livro antigo, cada página carrega séculos de mistério.", duration=4.0),
            Scene(order=2, narration_text="O fotógrafo ergue a câmera para registrar a imagem para a história.", duration=3.5)
        ]
        manifest = SoundFXAutoFoley.generate_plan_foley_manifest(plan)
        self.assertIn("total_foley_cues", manifest)
        self.assertIn("cues", manifest)
        self.assertGreaterEqual(manifest["total_foley_cues"], 1)

        categories = [c["category"] for c in manifest["cues"]]
        self.assertTrue(any(c in ["page_turn", "camera_shutter"] for c in categories))

if __name__ == "__main__":
    unittest.main()
