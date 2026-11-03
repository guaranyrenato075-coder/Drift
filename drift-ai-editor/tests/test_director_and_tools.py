import unittest
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, ProjectPlan, ProjectConfig, MediaCandidate
from director.command_editor import NaturalLanguageCommandEditor
from analysis.reference_analyzer import ReferenceVideoAnalyzer
from pipeline.delta_editor import DeltaReeditor
from director.orchestrator import AiDirectorOrchestrator
from editing.deliverables_packager import DeliverablesPackager

class TestDirectorAndTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_natural_language_command_parser(self):
        plan = ProjectPlan(title="Projeto Filosofia", config=ProjectConfig())
        plan.scenes = [
            Scene(order=1, narration_text="Frase 1", visual_description="Homem pensando", duration=4.0),
            Scene(order=2, narration_text="Frase 2", visual_description="Estrada vazia", duration=5.0)
        ]

        # 1. Test replace media command
        cmd1 = NaturalLanguageCommandEditor.parse_instruction("Troque a cena 2 por imagens do espaço profundo", plan)
        self.assertEqual(len(cmd1.actions), 1)
        self.assertEqual(cmd1.actions[0].action_type, "replace_scene_media")
        self.assertEqual(cmd1.actions[0].scene_order, 2)

        # 2. Test audio volume command
        cmd2 = NaturalLanguageCommandEditor.parse_instruction("Deixe a música mais baixa", plan)
        self.assertEqual(cmd2.actions[0].action_type, "adjust_audio")
        self.assertEqual(cmd2.actions[0].parameters["volume_change_db"], -6.0)

        # 3. Test pacing speedup
        cmd3 = NaturalLanguageCommandEditor.parse_instruction("Acelere o ritmo dos primeiros 20 segundos", plan)
        self.assertEqual(cmd3.actions[0].action_type, "adjust_pacing")
        self.assertEqual(cmd3.actions[0].parameters["limit_seconds"], 20.0)

        # Apply plan
        applied = NaturalLanguageCommandEditor.apply_plan(cmd1, plan)
        self.assertIn("Cena 2", applied[0])
        self.assertEqual(plan.scenes[1].visual_description, "imagens do espaço profundo")

    def test_reference_analyzer(self):
        dummy_video = self.temp_path / "reference_clip.mp4"
        dummy_video.write_bytes(b"0" * (1024 * 1024 * 30))  # 30MB

        analysis = ReferenceVideoAnalyzer.analyze_reference(str(dummy_video))
        self.assertGreater(analysis.total_duration_sec, 0)
        self.assertGreater(analysis.estimated_cuts_count, 1)
        self.assertIsNotNone(analysis.recommended_profile)
        self.assertIn("Estilo Referência", analysis.recommended_profile.name)

    def test_delta_reeditor(self):
        plan = ProjectPlan(title="Projeto Delta", config=ProjectConfig())
        s1 = Scene(order=1, narration_text="Texto inalterado", duration=4.0, audio_path="audio1.wav")
        s2 = Scene(order=2, narration_text="Texto que vai mudar", duration=4.0, audio_path="audio2.wav")
        plan.scenes = [s1, s2]

        updated_script = (
            "CENA 01\nNARRAÇÃO: Texto inalterado\nDESCRIÇÃO VISUAL: Visual 1\n\n"
            "CENA 02\nNARRAÇÃO: Novo texto totalmente reescrito\nDESCRIÇÃO VISUAL: Visual 2"
        )

        mod, add, rem = DeltaReeditor.apply_script_update(plan, updated_script)
        self.assertIn(2, mod)
        self.assertEqual(len(add), 0)
        self.assertEqual(len(rem), 0)

        # Verify scene 1 audio was preserved, but scene 2 audio was invalidated
        self.assertEqual(plan.scenes[0].audio_path, "audio1.wav")
        self.assertIsNone(plan.scenes[1].audio_path)

    def test_director_orchestrator(self):
        orchestrator = AiDirectorOrchestrator()
        plan = ProjectPlan(title="Projeto Orquestrado", config=ProjectConfig())
        plan.scenes = [Scene(order=1, narration_text="Cena teste", duration=4.0)]

        res = orchestrator.process_command(plan, "Troque a cena 1 por galáxias")
        self.assertTrue(res.success)
        self.assertEqual(res.agent_name, "CommandAgent")
        self.assertIn("Cena 1", res.summary)

    def test_deliverables_packager(self):
        plan = ProjectPlan(title="Como Vencer a Procrastinação", config=ProjectConfig())
        plan.scenes = [
            Scene(order=1, concept="Introdução", narration_text="Intro", duration=5.0),
            Scene(order=2, concept="O Método dos 5 Minutos", narration_text="Método", duration=10.0)
        ]

        kit = DeliverablesPackager.generate_release_kit(plan, output_dir=self.temp_path / "kit")
        self.assertEqual(kit["chapters_count"], 2)
        self.assertIn("00:00 Introdução", kit["chapters_text"])
        self.assertIn("00:05 O Método dos 5 Minutos", kit["chapters_text"])
        self.assertGreater(len(kit["title_variants"]), 1)
        self.assertTrue((self.temp_path / "kit" / "youtube_description.txt").exists())

if __name__ == "__main__":
    unittest.main()

