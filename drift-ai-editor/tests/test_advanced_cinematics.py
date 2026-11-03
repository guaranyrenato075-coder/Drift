"""
Unit tests for advanced cinematics and production tools:
CinematicColorLutDirector, AudioWaveformVisualizer, AxisRuleChecker,
TeleprompterEngine, SmartJumpCutter, YoutubeChapterGenerator,
MultiFormatExporter, VideoPodcastPublisher, PacingMetronome, AdaptiveBpmComposer.
"""
import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.cinematic_color_lut import CinematicColorLutDirector, ColorMoodProfile
from editing.audio_waveform_visualizer import AudioWaveformVisualizer, WaveformStyle
from analysis.axis_rule_checker import AxisRuleChecker, ScreenDirection
from voice.teleprompter_engine import TeleprompterEngine
from voice.smart_jump_cutter import SmartJumpCutter
from pipeline.youtube_chapter_generator import YoutubeChapterGenerator
from pipeline.multiformat_exporter import MultiFormatExporter, AspectTarget
from pipeline.video_podcast_publisher import VideoPodcastPublisher, PodcastEpisodeMetadata
from analysis.pacing_metronome import PacingMetronome, CadenceClassification
from audio.adaptive_bpm_composer import AdaptiveBpmComposer

class TestAdvancedCinematics(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(title="História das Civilizações")
        self.plan.scenes = [
            Scene(order=1, narration_text="No princípio das primeiras cidades antigas.", visual_description="Homem olhando para a direita", duration=3.5),
            Scene(order=2, narration_text="O comércio ligou impérios através de desertos e mares.", visual_description="Mercadores correndo para a direita", duration=4.0),
            Scene(order=3, narration_text="Mas conflitos épicos romperam a paz dos reinos.", visual_description="Exército marchando correndo para a esquerda", duration=8.0),
            Scene(order=4, narration_text="Hoje os monumentos permanecem como legado imortal.", visual_description="Ruínas ao amanhecer", duration=3.0)
        ]
        self.plan.reindex_scenes()

    def test_cinematic_color_lut(self):
        recipe = CinematicColorLutDirector.get_color_recipe(ColorMoodProfile.TEAL_AND_ORANGE)
        self.assertEqual(recipe.mood, ColorMoodProfile.TEAL_AND_ORANGE)
        self.assertIn("eq=saturation=1.25", recipe.ffmpeg_filter)
        self.assertIn("colorbalance=", recipe.ffmpeg_filter)

    def test_audio_waveform_visualizer(self):
        spec = AudioWaveformVisualizer.generate_visualizer_spec(WaveformStyle.FREQUENCY_BARS)
        self.assertEqual(spec.style, WaveformStyle.FREQUENCY_BARS)
        self.assertIn("showfreqs=", spec.ffmpeg_filter)

    def test_axis_rule_checker(self):
        report = AxisRuleChecker.audit_timeline(self.plan)
        self.assertEqual(report.total_cuts_audited, 3)
        # Scene 2 moving east, Scene 3 moving west -> violation alert!
        self.assertFalse(report.is_continuity_preserved)
        self.assertGreater(len(report.alerts), 0)
        self.assertEqual(report.alerts[0].severity, "critical")

    def test_teleprompter_engine(self):
        script = "Primeiro parágrafo do texto.\nSegundo parágrafo com mais conteúdo."
        session = TeleprompterEngine.prepare_session(script, target_wpm=150.0)
        self.assertEqual(len(session.cues), 2)
        self.assertGreater(session.total_words, 0)
        self.assertEqual(session.cues[1].scroll_position_pct, 100.0)

    def test_smart_jump_cutter(self):
        edl = SmartJumpCutter.analyze_audio_silences(
            duration=10.0,
            silence_intervals=[(2.0, 3.0), (6.5, 7.5)]
        )
        self.assertEqual(edl.total_cuts, 2)
        self.assertGreater(edl.time_saved, 1.5)
        self.assertIn("silenceremove=", edl.ffmpeg_silenceremove_filter)

    def test_youtube_chapter_generator(self):
        manifest = YoutubeChapterGenerator.generate_chapters(self.plan)
        self.assertGreaterEqual(manifest.total_chapters, 1)
        self.assertIn("00:00", manifest.description_block)
        self.assertIn(";FFMETADATA1", manifest.ffmpeg_metadata_manifest)

    def test_multiformat_exporter(self):
        batch = MultiFormatExporter.prepare_multiformat_batch("proj_1", "História")
        self.assertEqual(len(batch.specs), 3)
        targets = [s.target for s in batch.specs]
        self.assertIn(AspectTarget.LANDSCAPE_16_9, targets)
        self.assertIn(AspectTarget.VERTICAL_9_16, targets)
        self.assertIn(AspectTarget.SQUARE_1_1, targets)

    def test_video_podcast_publisher(self):
        episodes = [
            PodcastEpisodeMetadata(
                episode_id="ep1",
                title="Episódio 1: Origens",
                description="Descrição do episódio piloto.",
                video_file_url="https://cdn.example.com/ep1.mp4",
                file_size_bytes=104857600,
                duration_seconds=1200.0,
                pub_date="Fri, 30 Oct 2026 20:00:00 GMT",
                cover_art_url="https://cdn.example.com/cover.jpg"
            )
        ]
        rss = VideoPodcastPublisher.generate_rss_feed("Meu Canal", "Podcast oficial", "https://example.com", episodes)
        self.assertIn("<rss version=\"2.0\"", rss)
        self.assertIn("Episódio 1: Origens", rss)
        self.assertIn("enclosure url=", rss)

    def test_pacing_metronome(self):
        profile = PacingMetronome.analyze_pacing(self.plan)
        self.assertEqual(profile.total_cuts, 4)
        self.assertGreater(profile.average_shot_length_sec, 0)
        self.assertIn(profile.cadence, [CadenceClassification.DYNAMIC_ENGAGING, CadenceClassification.CINEMATIC_MEASURED])

    def test_adaptive_bpm_composer(self):
        composition = AdaptiveBpmComposer.compose_for_plan(self.plan)
        self.assertEqual(len(composition.sections), 4)
        self.assertGreater(composition.peak_bpm, composition.base_bpm)
        self.assertEqual(composition.sections[2].tension_level, "climax")

if __name__ == "__main__":
    unittest.main()

