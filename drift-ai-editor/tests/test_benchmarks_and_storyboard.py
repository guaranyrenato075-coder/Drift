import unittest
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, ProjectPlan, ProjectConfig, MediaCandidate
from media.diversity_controller import VisualDiversityController
from analysis.visual_storyboard import VisualStoryboardBuilder
from benchmarks.ai_bench import AiBenchHarness

class TestBenchmarksAndStoryboard(unittest.TestCase):

    def test_visual_diversity_controller(self):
        plan = ProjectPlan(title="Projeto Diversidade", config=ProjectConfig())
        # Simulate 4 consecutive scenes with identical creator and platform
        for i in range(1, 5):
            s = Scene(order=i, narration_text=f"Cena {i}", duration=4.0)
            s.selected_media = MediaCandidate(
                platform="pexels", external_id=str(i), creator="Repetitive Creator",
                title=f"Take {i}"
            )
            plan.scenes.append(s)

        audit = VisualDiversityController.audit_project_diversity(plan)
        self.assertFalse(audit.is_sufficiently_diverse)
        alert_cats = [a.category for a in audit.alerts]
        self.assertIn("creator_repetition", alert_cats)
        self.assertIn("platform_monotony", alert_cats)

    def test_visual_storyboard_builder(self):
        plan = ProjectPlan(title="Projeto Storyboard", config=ProjectConfig())
        s1 = Scene(order=1, narration_text="Narração cena 1", duration=5.0)
        s1.selected_media = MediaCandidate(platform="unsplash", external_id="u1", title="Sunrise", download_url="http://img.jpg")
        s2 = Scene(order=2, narration_text="Narração cena 2", duration=6.0)
        plan.scenes = [s1, s2]

        deck = VisualStoryboardBuilder.build_deck(plan)
        self.assertEqual(deck.cards_count, 2)
        self.assertEqual(deck.cards[0].scene_order, 1)
        self.assertEqual(deck.cards[0].primary_media_title, "Sunrise")

        # Test drag-and-drop reordering: [2, 1]
        VisualStoryboardBuilder.reorder_deck(plan, [2, 1])
        self.assertEqual(plan.scenes[0].order, 1)
        self.assertEqual(plan.scenes[0].duration, 6.0)  # former s2 is now first
        self.assertEqual(plan.scenes[1].duration, 5.0)  # former s1 is now second

    def test_ai_bench_harness(self):
        summary = AiBenchHarness.run_benchmark_suite()
        self.assertEqual(summary.total_scenarios, 3)
        self.assertEqual(summary.passed_scenarios, 3)
        self.assertEqual(summary.overall_health, "EXCELLENT")
        self.assertGreater(summary.average_execution_time_sec, 0.0)

        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "ai_bench_report.md"
            report_md = AiBenchHarness.generate_markdown_report(summary, out_file)
            self.assertIn("AI Bench", report_md)
            self.assertTrue(out_file.exists())

if __name__ == "__main__":
    unittest.main()

