"""
Unit tests for Gemini Skill Bridge and Loader in CutWire Drift AI.
"""
import unittest
import tempfile
from pathlib import Path
from skills.gemini_skill_bridge import GeminiSkillBridge, GeminiSkill

class TestGeminiSkillBridge(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.bridge = GeminiSkillBridge(skills_dir=Path(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_skills_installed(self):
        skills = self.bridge.list_skills()
        self.assertGreaterEqual(len(skills), 3)
        ids = [s["skill_id"] for s in skills]
        self.assertIn("documentary_master", ids)
        self.assertIn("viral_hook_crafter", ids)
        self.assertIn("cinematic_color_director", ids)

    def test_install_custom_skill(self):
        custom_md = """---
name: "Narrador Científico Quântico"
description: "Especialista em explicar física quântica e astrofísica com analogias do dia a dia."
version: "1.2.0"
author: "Pesquisador"
tags: ["fisica", "ciencia", "gemini"]
---

Você é um cientista explicando física de partículas. Use metáforas do cotidiano.
"""
        skill = self.bridge.install_skill_from_text(
            skill_name="Narrador Científico Quântico",
            description="Especialista em física quântica",
            markdown_content=custom_md
        )
        self.assertEqual(skill.name, "Narrador Científico Quântico")
        self.assertIn("metáforas do cotidiano", skill.system_instructions)

        # Check list includes it
        skills = self.bridge.list_skills()
        names = [s["name"] for s in skills]
        self.assertIn("Narrador Científico Quântico", names)

    def test_execute_skill(self):
        input_text = "Como funciona o entrelaçamento quântico?"
        output = self.bridge.execute_skill("documentary_master", input_text)
        self.assertIn("Roteirista de Documentário Imersivo", output)
        self.assertIn(input_text, output)

if __name__ == "__main__":
    unittest.main()

