"""
Unit tests for studio-grade innovations:
BokehDepthSimulator, VideoRestorationEngine, SplitScreenSlider,
FoleySoundDirector, VoiceEmotionShifter, ThumbnailAttentionHeatmap,
CreditsRollGenerator, FcpxmlExporter, AudioFirstCuttingEngine,
TransitionMonotonyDetector.
"""
import unittest
from models.scene_plan import ProjectPlan, Scene, MediaCandidate
from editing.bokeh_depth_simulator import BokehDepthSimulator, BokehIntensity
from editing.video_restoration_filter import VideoRestorationEngine, RestorationPreset
from editing.split_screen_slider import SplitScreenSlider, SplitOrientation
from audio.foley_sound_director import FoleySoundDirector, FoleyCategory
from voice.emotion_pitch_shifter import VoiceEmotionShifter, EmotionalState
from pipeline.thumbnail_attention_heatmap import ThumbnailAttentionHeatmap
from editing.credits_roll_generator import CreditsRollGenerator
from pipeline.fcpxml_exporter import FcpxmlExporter
from analysis.audio_first_cutting import AudioFirstCuttingEngine
from editing.transition_monotony_detector import TransitionMonotonyDetector

class TestStudioGradeInnovations(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(title="Mundo Antigo")
        s1 = Scene(order=1, narration_text="O filósofo caminhando pela cidade antiga.", visual_description="Homem caminhando na chuva", duration=3.0)
        s1.transition = "hard_cut"
        s2 = Scene(order=2, narration_text="Digitando os códigos no computador da biblioteca.", visual_description="Teclado e tela", duration=3.0)
        s2.transition = "hard_cut"
        s3 = Scene(order=3, narration_text="Lendo o livro antigo com páginas amareladas.", visual_description="Página de livro", duration=4.0)
        s3.transition = "hard_cut"
        s4 = Scene(order=4, narration_text="A porta do templo fechando para sempre.", visual_description="Porta de pedra", duration=4.0)
        s4.transition = "hard_cut"
        self.plan.scenes = [s1, s2, s3, s4]
        self.plan.reindex_scenes()

    def test_bokeh_depth_simulator(self):
        spec = BokehDepthSimulator.create_bokeh_filter(BokehIntensity.DREAMY_F1_4)
        self.assertEqual(spec.intensity, BokehIntensity.DREAMY_F1_4)
        self.assertIn("gblur=sigma=16.0", spec.ffmpeg_filter)

    def test_video_restoration_engine(self):
        spec = VideoRestorationEngine.get_restoration_filter(RestorationPreset.VINTAGE_ARCHIVE)
        self.assertIn("hqdn3d=", spec.ffmpeg_filter)
        self.assertIn("unsharp=", spec.ffmpeg_filter)

    def test_split_screen_slider(self):
        recipe = SplitScreenSlider.create_comparison_plan("a.mp4", "b.mp4", 4.0, "Passado", "Futuro")
        self.assertEqual(recipe.label_left, "Passado")
        self.assertIn("blend=", recipe.ffmpeg_complex_filter)

    def test_foley_sound_director(self):
        cues = FoleySoundDirector.schedule_foley(self.plan)
        self.assertGreater(len(cues), 2)
        cats = [c.category for c in cues]
        self.assertIn(FoleyCategory.FOOTSTEPS, cats)

    def test_voice_emotion_shifter(self):
        prof = VoiceEmotionShifter.get_modulation(EmotionalState.DRAMATIC_CLIMAX)
        self.assertGreater(prof.tempo_rate, 1.0)
        self.assertIn("rubberband=", prof.ffmpeg_rubberband_filter)

    def test_thumbnail_attention_heatmap(self):
        report = ThumbnailAttentionHeatmap.analyze_thumbnail(has_human_face=True, text_word_count=4)
        self.assertGreaterEqual(report.overall_ctr_score, 70)
        self.assertEqual(len(report.grid_matrix), 9)

    def test_credits_roll_generator(self):
        credits_plan = CreditsRollGenerator.generate_credits(self.plan, director_name="Studio Director")
        self.assertIn("Studio Director", credits_plan.raw_credits_text)
        self.assertIn("CRÉDITOS FINAIS", credits_plan.raw_credits_text)
        self.assertIn("drawtext=", credits_plan.ffmpeg_drawtext_filter)

    def test_fcpxml_exporter(self):
        xml_str = FcpxmlExporter.export_fcpxml(self.plan)
        self.assertIn("<fcpxml version=\"1.9\">", xml_str)
        self.assertIn("<clip name=\"Scene_01\"", xml_str)

    def test_audio_first_cutting(self):
        edit_plan = AudioFirstCuttingEngine.align_cuts_to_rhythm(self.plan, bpm=120)
        self.assertEqual(edit_plan.total_audio_cuts, 4)
        self.assertGreaterEqual(edit_plan.beat_sync_rate_pct, 0.0)

    def test_transition_monotony_detector(self):
        # 4 consecutive hard cuts should trigger a monotony alert!
        report = TransitionMonotonyDetector.audit_transitions(self.plan)
        self.assertFalse(report.is_diverse)
        self.assertGreater(len(report.alerts), 0)
        self.assertEqual(report.alerts[0].overused_transition, "hard_cut")

if __name__ == "__main__":
    unittest.main()

