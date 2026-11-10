import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.dynamic_subtitles_word_highlighter import DynamicSubtitlesWordHighlighter


class TestDynamicSubtitlesWordHighlighter(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Vídeo com Legendas Dinâmicas",
            scenes=[
                Scene(order=1, duration=4.0, narration_text="Descubra o segredo supremo da criação visual."),
                Scene(order=2, duration=3.5, narration_text="Isso muda completamente todo o jogo.")
            ]
        )

    def test_get_available_styles(self):
        styles = DynamicSubtitlesWordHighlighter.get_available_styles()
        self.assertIn("hormozi_bold_yellow", styles)
        self.assertIn("mrbeast_impact_green", styles)
        self.assertIn("minimal_cinema_white", styles)
        self.assertIn("cyberpunk_neon_cyan", styles)

    def test_generate_ass_subtitle_content(self):
        res = DynamicSubtitlesWordHighlighter.generate_ass_subtitle_content(self.plan, "hormozi_bold_yellow")
        self.assertEqual(res["total_dialogue_events"], 2)
        ass = res["ass_content"]
        self.assertIn("[Script Info]", ass)
        self.assertIn("[V4+ Styles]", ass)
        self.assertIn("Dialogue: 0,", ass)
        self.assertIn(r"{\k", ass)  # Tag karaoke de realce por palavra


if __name__ == "__main__":
    unittest.main()
