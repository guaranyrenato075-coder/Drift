"""
Unit tests for AITranscriptionSubtitleStyler in Drift AI.
Verifies ASS subtitle presets, typography styles, time formatting, and script generation.
"""
import unittest
import tempfile
from pathlib import Path
from editing.subtitle_styler import AITranscriptionSubtitleStyler, SubtitleStylePreset
from models.scene_plan import ProjectPlan, Scene

class TestSubtitleStyler(unittest.TestCase):

    def test_list_styles(self):
        styles = AITranscriptionSubtitleStyler.list_styles()
        self.assertGreaterEqual(len(styles), 4)
        style_ids = {s["id"] for s in styles}
        self.assertIn("hormozi_viral", style_ids)
        self.assertIn("neon_glow", style_ids)
        self.assertIn("cinema_classic", style_ids)
        self.assertIn("minimalist_clean", style_ids)

    def test_format_ass_time(self):
        self.assertEqual(AITranscriptionSubtitleStyler.format_ass_time(0.0), "0:00:00.00")
        self.assertEqual(AITranscriptionSubtitleStyler.format_ass_time(65.45), "0:01:05.45")

    def test_generate_styled_ass_content(self):
        plan = ProjectPlan(title="Teste Legenda")
        plan.scenes = [
            Scene(order=1, narration_text="Esta é a frase viral mais incrível de todas.", duration=4.0)
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "test.ass"
            content = AITranscriptionSubtitleStyler.generate_styled_ass(plan, style_id="hormozi_viral", output_path=str(out_file))

            self.assertTrue(out_file.exists())
            self.assertIn("[Script Info]", content)
            self.assertIn("[V4+ Styles]", content)
            self.assertIn("Style: Default,Montserrat ExtraBold", content)
            self.assertIn("Dialogue:", content)

if __name__ == "__main__":
    unittest.main()
