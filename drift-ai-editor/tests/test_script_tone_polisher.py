"""
Unit tests for ScriptTonePolisher in Drift AI.
Verifies tone archetypes, viral hook prepending, and plan-wide stylistic polishing.
"""
import unittest
from analysis.script_tone_polisher import ScriptTonePolisher
from models.scene_plan import ProjectPlan, Scene

class TestScriptTonePolisher(unittest.TestCase):

    def test_list_tone_profiles(self):
        profiles = ScriptTonePolisher.list_tone_profiles()
        self.assertGreaterEqual(len(profiles), 4)
        p_ids = {p["id"] for p in profiles}
        self.assertIn("shorts_viral", p_ids)
        self.assertIn("bbc_documentary", p_ids)
        self.assertIn("mystery_investigation", p_ids)
        self.assertIn("didactic_friendly", p_ids)

    def test_polish_text_shorts_viral(self):
        raw = "o universo é muito grande e bastante interessante"
        polished = ScriptTonePolisher.polish_text(raw, tone_id="shorts_viral")
        self.assertIn("Você não vai acreditar nisso", polished)
        self.assertNotIn(" muito ", polished)
        self.assertNotIn(" bastante ", polished)

    def test_polish_plan(self):
        plan = ProjectPlan(title="Projeto Mistério")
        plan.scenes = [
            Scene(order=1, narration_text="Algo estranho aconteceu naquela noite."),
            Scene(order=2, narration_text="Nenhum cientista soube explicar o fenômeno.")
        ]
        polished_plan = ScriptTonePolisher.polish_plan(plan, tone_id="mystery_investigation")
        self.assertIn("Tudo parecia normal", polished_plan.scenes[0].narration_text)

if __name__ == "__main__":
    unittest.main()
