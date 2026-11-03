import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, SceneState, ProjectPlan, ProjectConfig
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from analysis.script_generator import ScriptGenerator

class TestScriptSegmenter(unittest.TestCase):

    def test_parse_structured_script(self):
        script = """
        CENA 01
        NARRAÇÃO: Você não controla tudo o que acontece.
        DESCRIÇÃO VISUAL: Um homem observa uma tempestade pela janela.
        DURAÇÃO: 4s

        CENA 02
        NARRAÇÃO: Mas pode controlar a maneira como reage.
        DESCRIÇÃO VISUAL: Uma pessoa caminha sozinha ao amanhecer.
        DURAÇÃO: automática.
        """
        self.assertTrue(ScriptSegmenter.is_structured(script))
        scenes = ScriptSegmenter.parse(script, default_language="pt", default_voice="default")

        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes[0].order, 1)
        self.assertEqual(scenes[0].narration_text, "Você não controla tudo o que acontece.")
        self.assertEqual(scenes[0].visual_description, "Um homem observa uma tempestade pela janela.")
        self.assertEqual(scenes[0].duration, 4.0)

        self.assertEqual(scenes[1].order, 2)
        self.assertEqual(scenes[1].narration_text, "Mas pode controlar a maneira como reage.")
        self.assertEqual(scenes[1].visual_description, "Uma pessoa caminha sozinha ao amanhecer.")
        self.assertEqual(scenes[1].duration, 0.0) # auto duration

    def test_parse_continuous_script(self):
        script = """
        A disciplina transforma suas escolhas diárias. Com pequenos passos, grandes mudanças se consolidam ao longo dos anos.
        
        O tempo revela o que realmente importa. Viva com propósito e clareza.
        """
        self.assertFalse(ScriptSegmenter.is_structured(script))
        scenes = ScriptSegmenter.parse(script, default_language="pt")

        self.assertGreaterEqual(len(scenes), 3)
        self.assertEqual(scenes[0].order, 1)
        self.assertTrue(scenes[0].narration_text.startswith("A disciplina"))
        for s in scenes:
            self.assertEqual(s.state, SceneState.PENDING)

    def test_empty_and_whitespace_input(self):
        self.assertEqual(ScriptSegmenter.parse(""), [])
        self.assertEqual(ScriptSegmenter.parse("    \n\n  \t "), [])

    def test_visual_planner(self):
        scene = Scene(
            order=1,
            narration_text="Você não controla tudo o que acontece na tempestade.",
            visual_description=""
        )
        VisualPlanner.plan_scene(scene)

        # Should infer visual description and keywords
        self.assertTrue(len(scene.visual_description) > 0)
        self.assertIn("tempestade", scene.visual_description.lower())
        self.assertTrue(len(scene.keywords) > 0)
        self.assertTrue(len(scene.english_keywords) > 0)
        self.assertIn("storm", [k.lower() for k in scene.english_keywords] + [k.lower() for k in scene.keywords])

    def test_script_generator(self):
        script = ScriptGenerator.generate("estoicismo")
        self.assertTrue(ScriptSegmenter.is_structured(script))
        scenes = ScriptSegmenter.parse(script)
        self.assertGreaterEqual(len(scenes), 3)
        self.assertTrue(any("controla" in s.narration_text.lower() for s in scenes))

    def test_project_plan_reindexing(self):
        plan = ProjectPlan(title="Teste Reindex")
        s1 = Scene(order=1, duration=5.0)
        s2 = Scene(order=2, duration=3.5)
        plan.scenes = [s1, s2]
        plan.reindex_scenes()

        self.assertEqual(plan.scenes[0].start_time, 0.0)
        self.assertEqual(plan.scenes[0].end_time, 5.0)
        self.assertEqual(plan.scenes[1].start_time, 5.0)
        self.assertEqual(plan.scenes[1].end_time, 8.5)
        self.assertEqual(plan.total_duration(), 8.5)

if __name__ == "__main__":
    unittest.main()

