import unittest
import tempfile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, SceneState, ProjectPlan, ProjectConfig, Provenance, MediaCandidate
from storage.repository import ProjectRepository

class TestStorageRepository(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_projects.db"
        self.repo = ProjectRepository(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_retrieve_project(self):
        plan = ProjectPlan(
            title="Projeto Teste 1",
            raw_script="Texto original do roteiro...",
            config=ProjectConfig(aspect_ratio="9:16", style="dynamic", language="pt", exaggeration=0.7)
        )
        plan.config.update_resolution()
        self.assertEqual(plan.config.width, 1080)
        self.assertEqual(plan.config.height, 1920)

        s1 = Scene(
            order=1,
            narration_text="Cena de abertura.",
            visual_description="Amanhecer no horizonte.",
            duration=4.2,
            provenance=Provenance(platform="pexels", item_id="12345", creator="John Doe")
        )
        s1.candidates.append(MediaCandidate(platform="pexels", external_id="12345", title="Sunrise"))
        s1.selected_media = s1.candidates[0]
        s1.state = SceneState.READY

        plan.scenes.append(s1)
        plan.reindex_scenes()

        # Save to database
        self.repo.save(plan)

        # Retrieve
        loaded_plan = self.repo.get(plan.project_id)
        self.assertIsNotNone(loaded_plan)
        self.assertEqual(loaded_plan.title, "Projeto Teste 1")
        self.assertEqual(loaded_plan.config.aspect_ratio, "9:16")
        self.assertEqual(loaded_plan.config.exaggeration, 0.7)
        self.assertEqual(len(loaded_plan.scenes), 1)

        scene = loaded_plan.scenes[0]
        self.assertEqual(scene.narration_text, "Cena de abertura.")
        self.assertEqual(scene.duration, 4.2)
        self.assertEqual(scene.state, SceneState.READY)
        self.assertEqual(scene.provenance.platform, "pexels")
        self.assertEqual(scene.selected_media.external_id, "12345")

    def test_update_scene_preserves_others(self):
        plan = ProjectPlan(title="Projeto Preservação")
        s1 = Scene(order=1, narration_text="Primeira fala", duration=3.0, state=SceneState.READY)
        s2 = Scene(order=2, narration_text="Segunda fala", duration=5.0, state=SceneState.READY)
        plan.scenes = [s1, s2]
        self.repo.save(plan)

        # Modify only s1
        loaded = self.repo.get(plan.project_id)
        loaded.scenes[0].narration_text = "Primeira fala alterada"
        loaded.scenes[0].state = SceneState.PENDING
        self.repo.save(loaded)

        reloaded = self.repo.get(plan.project_id)
        self.assertEqual(reloaded.scenes[0].narration_text, "Primeira fala alterada")
        self.assertEqual(reloaded.scenes[0].state, SceneState.PENDING)
        # s2 is preserved untouched!
        self.assertEqual(reloaded.scenes[1].narration_text, "Segunda fala")
        self.assertEqual(reloaded.scenes[1].state, SceneState.READY)
        self.assertEqual(reloaded.scenes[1].duration, 5.0)

    def test_export_import_json(self):
        plan = ProjectPlan(title="Projeto JSON")
        plan.scenes.append(Scene(order=1, narration_text="Teste de exportação"))
        json_file = Path(self.temp_dir.name) / "project_export.json"

        ProjectRepository.export_to_file(plan, json_file)
        self.assertTrue(json_file.exists())

        imported_plan = ProjectRepository.import_from_file(json_file)
        self.assertEqual(imported_plan.title, "Projeto JSON")
        self.assertEqual(len(imported_plan.scenes), 1)
        self.assertEqual(imported_plan.scenes[0].narration_text, "Teste de exportação")

if __name__ == "__main__":
    unittest.main()

