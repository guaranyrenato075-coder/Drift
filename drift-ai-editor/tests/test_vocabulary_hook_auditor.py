"""
Unit tests for ViralHookVocabularyAuditor in CutWire Drift AI.
Verifies passive phrase detection, neuro-linguistic scoring, and automated script replacement.
"""
import unittest
from analysis.vocabulary_hook_auditor import ViralHookVocabularyAuditor
from models.scene_plan import ProjectPlan, Scene

class TestVocabularyHookAuditor(unittest.TestCase):

    def test_audit_script_vocabulary_detects_cliches(self):
        plan = ProjectPlan(title="Roteiro com Clichês")
        plan.scenes = [
            Scene(order=1, narration_text="É interessante notar que o imperador hesitou."),
            Scene(order=2, narration_text="Com o passar do tempo, uma catástrofe ocorreu.")
        ]

        res = ViralHookVocabularyAuditor.audit_script_vocabulary(plan)
        self.assertEqual(res["total_weak_phrases_found"], 2)
        self.assertLess(res["neuro_linguistic_score"], 100)

        issues = res["issues"]
        self.assertEqual(issues[0]["weak_phrase"], "é interessante notar")
        self.assertEqual(issues[0]["suggested_replacement"], "o que ninguém esperava é que")

    def test_auto_enhance_script_vocabulary(self):
        plan = ProjectPlan(title="Roteiro para Polimento")
        plan.scenes = [
            Scene(order=1, narration_text="É interessante notar o fato histórico.")
        ]

        enh_res = ViralHookVocabularyAuditor.auto_enhance_script_vocabulary(plan)
        self.assertEqual(enh_res["total_phrases_enhanced"], 1)
        self.assertIn("o que ninguém esperava é que", plan.scenes[0].narration_text)

if __name__ == '__main__':
    unittest.main()
