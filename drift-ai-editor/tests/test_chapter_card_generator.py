"""
Unit tests for AutoVideoChapterCardGenerator in CutWire Drift AI.
Verifies Roman numeral mapping and cinematic motion graphic chapter card generation.
"""
import unittest
from editing.chapter_card_generator import AutoVideoChapterCardGenerator
from models.scene_plan import ProjectPlan, ProjectConfig

class TestChapterCardGenerator(unittest.TestCase):

    def test_generate_chapter_card(self):
        card = AutoVideoChapterCardGenerator.generate_chapter_card(
            index=2,
            title="O Nascimento das Estrelas",
            duration=3.0,
            width=1920,
            height=1080
        )

        self.assertEqual(card.chapter_index, 2)
        self.assertEqual(card.roman_numeral, "II")
        self.assertIn("CAPÍTULO II", card.ffmpeg_drawtext_filter)
        self.assertIn("O NASCIMENTO DAS ESTRELAS", card.ffmpeg_drawtext_filter)
        self.assertIn("gold", card.ffmpeg_drawtext_filter)
        self.assertIn("sub_boom", card.foley_sound_effect)

    def test_generate_cards_for_plan(self):
        plan = ProjectPlan(title="Cosmologia Moderna")
        plan.config = ProjectConfig(width=1920, height=1080)
        plan.config.extra = {
            "chapter_titles": ["O Início", "A Expansão", "O Futuro"]
        }

        res = AutoVideoChapterCardGenerator.generate_cards_for_plan(plan)
        self.assertEqual(res["total_chapter_cards"], 3)
        self.assertEqual(len(res["cards"]), 3)
        self.assertEqual(res["cards"][0]["roman_numeral"], "I")
        self.assertEqual(res["cards"][1]["roman_numeral"], "II")
        self.assertEqual(res["cards"][2]["roman_numeral"], "III")

if __name__ == '__main__':
    unittest.main()
