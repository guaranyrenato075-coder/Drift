"""
Unit test suite for CutWire Drift AI Mega-Duration Architecture (>20 to 120 minutes).
Verifies multi-chapter hierarchical planning, atomic lifecycle rendering,
ram-flush boundaries, FFmpeg lossless concatenation, and script generation.
"""
import unittest
import os
import sys

from pipeline.mega_duration_architect import (
    MegaDurationArchitect,
    MegaProductionPlan,
    MegaChapter
)
from analysis.script_generator import ScriptGenerator
from pipeline.chunked_parallel_renderer import ChunkedParallelRenderer
from models.scene_plan import Scene, SceneState

class TestMegaDurationProduction(unittest.TestCase):

    def test_mega_duration_planning_30_minutes(self):
        """Verifies hierarchical multi-chapter planning for a 30-minute documentary."""
        plan = MegaDurationArchitect.plan_mega_production(
            topic="O Mistério dos Buracos Negros",
            target_minutes=30.0,
            output_dir="d:/CUTWIREDRIFT/renders"
        )
        self.assertIsInstance(plan, MegaProductionPlan)
        self.assertEqual(plan.target_duration_minutes, 30.0)
        self.assertGreaterEqual(plan.total_chapters, 5)
        self.assertGreaterEqual(plan.total_scenes, 150)
        self.assertGreaterEqual(plan.estimated_total_duration_sec, 1700.0)
        self.assertEqual(plan.ram_budget_mb, 250.0)

        # Valida primeiro capítulo
        ch1 = plan.chapters[0]
        self.assertEqual(ch1.chapter_index, 1)
        self.assertTrue(ch1.intermediate_master_file.endswith(".mp4"))
        self.assertTrue(len(ch1.cliffhanger_hook) > 0)
        self.assertFalse(ch1.is_completed)

    def test_mega_duration_planning_60_minutes(self):
        """Verifies hierarchical multi-chapter planning for a 60-minute long-form essay."""
        plan = MegaDurationArchitect.plan_mega_production(
            topic="A Queda dos Grandes Impérios",
            target_minutes=60.0,
            output_dir="d:/CUTWIREDRIFT/renders"
        )
        self.assertEqual(plan.target_duration_minutes, 60.0)
        self.assertEqual(plan.total_chapters, 8)
        self.assertGreaterEqual(plan.total_scenes, 300)
        self.assertGreaterEqual(plan.estimated_total_duration_sec, 3500.0)

        # Checa progressão de humores sonoros entre capítulos
        moods = [c.soundtrack_mood for c in plan.chapters]
        self.assertGreater(len(set(moods)), 3)

    def test_concat_manifest_and_lossless_ffmpeg_command(self):
        """Ensures FFmpeg manifest and sub-second stream copy command are accurately formatted."""
        plan = MegaDurationArchitect.plan_mega_production(
            topic="A Revolução da Inteligência Artificial",
            target_minutes=30.0,
            output_dir="d:/CUTWIREDRIFT/renders"
        )
        manifest_text = MegaDurationArchitect.generate_concat_manifest(plan)
        self.assertIn("# Drift AI Mega-Duration Hierarchical Stitch Manifest", manifest_text)
        for ch in plan.chapters:
            self.assertIn(f"file '{ch.intermediate_master_file}'", manifest_text)

        cmd = MegaDurationArchitect.get_ffmpeg_stitching_command(
            manifest_path="d:/CUTWIREDRIFT/renders/concat.txt",
            final_output_path="d:/CUTWIREDRIFT/renders/final.mp4"
        )
        self.assertIn("-c", cmd)
        self.assertIn("copy", cmd)
        self.assertIn("-f", cmd)
        self.assertIn("concat", cmd)

    def test_atomic_chapter_render_lifecycle_with_ram_flush(self):
        """Verifies chapter rendering lifecycle with thermal duty cycle and RAM release."""
        plan = MegaDurationArchitect.plan_mega_production(
            topic="O Futuro da Consciência",
            target_minutes=25.0
        )
        res = MegaDurationArchitect.simulate_chapter_render_lifecycle(plan, chapter_index=1)
        self.assertEqual(res["chapter_index"], 1)
        self.assertEqual(res["status"], "ready_for_concatenation")
        self.assertIn("ram_flushed_mb", res)
        self.assertTrue(plan.chapters[0].is_completed)

        # Out of bounds index
        with self.assertRaises(IndexError):
            MegaDurationArchitect.simulate_chapter_render_lifecycle(plan, chapter_index=99)

    def test_script_generator_mega_doc_expansion(self):
        """Verifies ScriptGenerator produces multi-act scenes for mega documentaries."""
        script_mega = ScriptGenerator.generate(
            topic="tecnologia",
            duration_type="mega_doc",
            duration_minutes=30.0
        )
        self.assertIn("CENA 01", script_mega)
        self.assertIn("CENA 10", script_mega)
        self.assertIn("CENA 20", script_mega)
        self.assertIn("Bloco", script_mega)

    def test_chunked_parallel_renderer_chapter_plan(self):
        """Verifies ChunkedParallelRenderer can partition an isolated chapter into parallel chunks."""
        scenes = [
            Scene(order=i, narration_text=f"Cena {i}", duration=8.0, state=SceneState.READY)
            for i in range(1, 16)  # 15 cenas * 8s = 120s
        ]
        plan = ChunkedParallelRenderer.create_chapter_render_plan(
            scenes=scenes,
            chapter_title="Capitulo 1: O Inicio",
            output_master_file="d:/CUTWIREDRIFT/renders/chap_01_master.mp4",
            target_chunk_sec=24.0
        )
        self.assertEqual(plan.total_scenes, 15)
        self.assertGreaterEqual(plan.total_chunks, 5)
        self.assertEqual(plan.final_output_path, "d:/CUTWIREDRIFT/renders/chap_01_master.mp4")

if __name__ == "__main__":
    unittest.main()
