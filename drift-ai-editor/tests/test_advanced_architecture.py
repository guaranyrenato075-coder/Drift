import unittest
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.dependency_graph import ProjectDependencyGraph
from core.transaction_manager import UnifiedOperationController, AtomicOperation
from core.production_memory import ProductionMemoryManager
from media.semantic_search import SemanticLocalSearch
from analysis.continuity_checker import VisualContinuityDirector
from analysis.storyboard_engine import VisualIntent
from models.scene_plan import Scene, ProjectPlan, ProjectConfig
from pipeline.batch_producer import BatchProductionEngine, SeriesEpisodeInput

class TestAdvancedArchitecture(unittest.TestCase):

    def test_dependency_graph_and_impact(self):
        dag = ProjectDependencyGraph("proj_dag_1")
        # Add scene node and its audio and video file dependencies
        s1 = dag.add_node("scene_1", "scene", "Cena 01", {"order": 1})
        a1 = dag.add_node("audio_1", "audio", "Voz Cena 1", {"file_path": "C:/audio/cena1.wav"})
        v1 = dag.add_node("video_1", "video_asset", "Take Espaço", {"file_path": "D:/videos/space.mp4"})
        clip1 = dag.add_node("clip_1", "timeline_clip", "Clip V1 na Timeline")

        # Establish DAG edges: video_1 -> clip1, s1 -> a1, s1 -> clip1
        dag.add_dependency("video_1", "clip_1")
        dag.add_dependency("scene_1", "audio_1")
        dag.add_dependency("scene_1", "clip_1")

        # Invalidate scene_1 -> clip_1 and audio_1 must become dirty
        dirty = dag.mark_dirty("scene_1")
        self.assertIn("audio_1", dirty)
        self.assertIn("clip_1", dirty)

        # Query file impact: if D:/videos/space.mp4 is missing, pinpoint video_1 and clip_1
        impacted = dag.query_file_impact("D:/videos/space.mp4")
        impacted_ids = [n.node_id for n in impacted]
        self.assertIn("video_1", impacted_ids)
        self.assertIn("clip_1", impacted_ids)

    def test_unified_transaction_controller(self):
        controller = UnifiedOperationController("proj_tx_1")
        controller.lock_user_edit("scene_user_locked")

        op_ai = AtomicOperation(
            action="replace_media",
            target_scene_id="scene_user_locked",
            parameters={"query": "galaxy"},
            is_ai_generated=True,
            description="Tentativa de sobreposição pela IA"
        )
        op_valid = AtomicOperation(
            action="replace_media",
            target_scene_id="scene_normal",
            parameters={"query": "ocean"},
            inverse_parameters={"query": "original"},
            is_ai_generated=True,
            description="Alteração permitida"
        )

        tx = controller.execute_transaction("Edição Automática", [op_ai, op_valid])
        # op_ai must be filtered out because scene_user_locked is protected
        self.assertEqual(len(tx.operations), 1)
        self.assertEqual(tx.operations[0].target_scene_id, "scene_normal")

        # Test Rollback
        reverted = controller.rollback_transaction(tx.transaction_id)
        self.assertTrue(reverted)
        self.assertTrue(tx.is_reverted)

    def test_semantic_local_search(self):
        dummy_catalog = [
            {"path": "D:/acervo/man_walking_rain_night.mp4", "filename": "man_walking_rain_night.mp4", "keywords": ["chuva", "caminhando", "sozinho"], "type": "video"},
            {"path": "D:/acervo/deep_galaxy_stars_4k.mp4", "filename": "deep_galaxy_stars_4k.mp4", "keywords": ["universo", "espaço", "planeta"], "type": "video"}
        ]
        searcher = SemanticLocalSearch(dummy_catalog)
        results = searcher.search_by_meaning("homem caminhando na chuva")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].external_id, "man_walking_rain_night")

    def test_production_memory(self):
        with tempfile.TemporaryDirectory() as td:
            mem_file = Path(td) / "user_memory.json"
            pm = ProductionMemoryManager(memory_file=mem_file)
            pm.record_decision("transition_preferred", "dissolve")
            pm.record_decision("pacing_changed", 1.25)
            pm.record_decision("transition_rejected", "flash_white")

            self.assertEqual(pm.preferences.preferred_transition, "dissolve")
            self.assertEqual(pm.preferences.preferred_pacing_bias, 1.25)
            self.assertIn("flash_white", pm.preferences.prohibited_transitions)

            # Re-load from disk to verify persistence
            pm_reloaded = ProductionMemoryManager(memory_file=mem_file)
            self.assertEqual(pm_reloaded.preferences.preferred_transition, "dissolve")

    def test_visual_continuity_director(self):
        scenes = [
            Scene(order=1, narration_text="Intro", duration=4.0),
            Scene(order=2, narration_text="Take 2", duration=4.0),
            Scene(order=3, narration_text="Take 3", duration=4.0)
        ]
        # Simulate 3 identical close-up shots (framing fatigue)
        intents = {
            1: VisualIntent(scene_order=1, core_concept="A", emotional_tone="hesitation", shot_type="close_up", camera_movement="static", semantic_intent="A", search_queries=[], negative_tags=[], quality_criteria=""),
            2: VisualIntent(scene_order=2, core_concept="B", emotional_tone="hesitation", shot_type="close_up", camera_movement="static", semantic_intent="B", search_queries=[], negative_tags=[], quality_criteria=""),
            3: VisualIntent(scene_order=3, core_concept="C", emotional_tone="hesitation", shot_type="close_up", camera_movement="static", semantic_intent="C", search_queries=[], negative_tags=[], quality_criteria="")
        }

        report = VisualContinuityDirector.audit_visual_continuity(scenes, intents)
        self.assertFalse(report.is_cinematically_sound)
        alerts_types = [a.alert_type for a in report.alerts]
        self.assertIn("framing_fatigue", alerts_types)

    def test_batch_production_series(self):
        with tempfile.TemporaryDirectory() as td:
            from storage.repository import ProjectRepository
            repo = ProjectRepository(db_path=Path(td) / "series.db")
            engine = BatchProductionEngine(repo=repo)

            episodes = [
                SeriesEpisodeInput(title="Episódio 1", script_text="CENA 01\nNARRAÇÃO: Início da jornada\nDESCRIÇÃO VISUAL: Estrada ao amanhecer", episode_number=1),
                SeriesEpisodeInput(title="Episódio 2", script_text="CENA 01\nNARRAÇÃO: O desafio final\nDESCRIÇÃO VISUAL: Montanha íngreme", episode_number=2)
            ]

            result = engine.process_series("Jornada Estóica", episodes, style_id="filosofico")
            self.assertEqual(result.total_episodes, 2)
            self.assertEqual(result.completed_episodes, 2)
            self.assertEqual(len(result.project_ids), 2)

if __name__ == "__main__":
    unittest.main()

