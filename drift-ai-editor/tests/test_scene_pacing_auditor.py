"""
Unit tests for ScenePacingAuditor in Drift AI.
Verifies speech velocity (WPM), scene monotony risk detection, and retention scoring.
"""
import unittest
from analysis.scene_pacing_auditor import ScenePacingAuditor, ScenePacingMetric, PacingAuditReport
from models.scene_plan import ProjectPlan, Scene

class TestScenePacingAuditor(unittest.TestCase):

    def test_audit_scene_optimal(self):
        scene = Scene(
            order=1,
            narration_text="Esta é uma frase perfeita com ritmo excelente para o espectador.",
            duration=4.5
        )
        metric = ScenePacingAuditor.audit_scene(scene)
        self.assertIsInstance(metric, ScenePacingMetric)
        self.assertGreater(metric.wpm, 100.0)
        self.assertEqual(metric.risk_level, "safe")

    def test_audit_scene_monotony(self):
        scene = Scene(
            order=2,
            narration_text="Cena parada.",
            duration=10.0
        )
        metric = ScenePacingAuditor.audit_scene(scene)
        self.assertEqual(metric.pacing_status, "monotonous")
        self.assertEqual(metric.risk_level, "high")
        self.assertIn("Divida em 2 cortes", metric.actionable_recommendation)

    def test_audit_plan_report(self):
        plan = ProjectPlan(title="Auditoria de Retenção")
        plan.scenes = [
            Scene(order=1, narration_text="Introdução dinâmica com muitas palavras para manter o ritmo rápido.", duration=4.0),
            Scene(order=2, narration_text="Segunda cena com boa velocidade e clareza visual.", duration=4.0)
        ]
        report = ScenePacingAuditor.audit_plan(plan)
        self.assertIsInstance(report, PacingAuditReport)
        self.assertGreaterEqual(report.overall_retention_score, 80)
        self.assertEqual(report.total_scenes_analyzed, 2)
        self.assertEqual(report.monotonous_scenes_count, 0)

if __name__ == "__main__":
    unittest.main()
