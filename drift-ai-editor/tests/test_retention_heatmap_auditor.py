"""
Unit tests for VisualRetentionHeatmapAuditor in CutWire Drift AI.
Verifies retention curve simulation, static scene drop-off risk detection, and auto-remediation.
"""
import unittest
from analysis.retention_heatmap_auditor import VisualRetentionHeatmapAuditor
from models.scene_plan import ProjectPlan, Scene

class TestVisualRetentionHeatmapAuditor(unittest.TestCase):

    def test_audit_retention_curve_detects_long_static_scenes(self):
        plan = ProjectPlan(title="Documentário de Teste de Retenção")
        plan.scenes = [
            Scene(order=1, narration_text="Introdução dinâmica.", duration=2.5),
            Scene(order=2, narration_text="Uma cena que dura tempo excessivo sem variação visual.", duration=6.0),
            Scene(order=3, narration_text="Conclusão com ritmo normal.", duration=2.8)
        ]

        result = VisualRetentionHeatmapAuditor.audit_retention_curve(plan)

        self.assertEqual(result["project_id"], plan.project_id)
        self.assertGreaterEqual(result["total_risk_zones_found"], 1)

        first_risk = result["risk_zones"][0]
        self.assertEqual(first_risk["scene_order"], 2)
        self.assertEqual(first_risk["risk_level"], "ALTO")
        self.assertIn("B-Roll", first_risk["remediation_suggestion"])

        self.assertGreater(len(result["retention_curve_sample"]), 0)
        self.assertLessEqual(result["average_predicted_retention_pct"], 100.0)

    def test_auto_remediate_plan_pacing(self):
        plan = ProjectPlan(title="Plano com Risco")
        plan.scenes = [
            Scene(order=1, duration=5.5),
            Scene(order=2, duration=2.0)
        ]

        res = VisualRetentionHeatmapAuditor.auto_remediate_plan_pacing(plan)
        self.assertEqual(res["remediated_scenes_count"], 1)
        self.assertEqual(plan.scenes[0].camera_motion, "dynamic_punch_in")

if __name__ == '__main__':
    unittest.main()
