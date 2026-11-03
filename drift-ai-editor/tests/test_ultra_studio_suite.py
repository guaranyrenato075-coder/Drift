"""
Unit tests for ultra-studio suite:
DepthTitleCompositor, YoutubeEndscreenDesigner, AudioMonotonyBreaker,
BRollAudioLeveler, MultilingualSubtitlesBundle, AutoSummarizerCut,
CopyrightSafeShield, SeoTagArchitect, GenreMorphingEngine, BatterySaverEngine.
"""
import unittest
from models.scene_plan import ProjectPlan, Scene, MediaCandidate
from editing.depth_title_compositor import DepthTitleCompositor
from editing.youtube_endscreen_designer import YoutubeEndscreenDesigner
from audio.audio_monotony_breaker import AudioMonotonyBreaker, MonotonyBreakerType
from audio.b_roll_audio_leveler import BRollAudioLeveler
from editing.multilingual_subtitles import MultilingualSubtitlesBundle
from pipeline.auto_summarizer_cut import AutoSummarizerCut
from media.copyright_shield import CopyrightSafeShield
from pipeline.seo_tag_architect import SeoTagArchitect
from audio.genre_morphing_engine import GenreMorphingEngine, MusicGenre
from core.battery_saver_mode import BatterySaverEngine, PowerState

class TestUltraStudioSuite(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(title="História dos Oceanos")
        s1 = Scene(order=1, narration_text="As profundezas azuis escondem segredos nunca vistos.", visual_description="Ondas gigantes no mar tempestuoso", duration=5.0)
        s1.selected_media = MediaCandidate("pexels", "101", "Ocean Waves", "", "", "John Diver", "", "Free")
        s2 = Scene(order=2, narration_text="Cientistas mapearam novas espécies de criaturas marinhas.", visual_description="Peixes abissais brilhantes", duration=6.0)
        s3 = Scene(order=3, narration_text="E a preservação ambiental tornou-se a grande missão.", visual_description="Recife de coral protegido", duration=6.0)
        self.plan.scenes = [s1, s2, s3]
        self.plan.reindex_scenes()

    def test_depth_title_compositor(self):
        spec = DepthTitleCompositor.create_depth_title("OCEANOS", 0.0, 4.0)
        self.assertEqual(spec.title_text, "OCEANOS")
        self.assertEqual(spec.z_layer, "behind_subject")
        self.assertIn("drawtext=text='OCEANOS'", spec.ffmpeg_filter_graph)

    def test_youtube_endscreen_designer(self):
        design = YoutubeEndscreenDesigner.generate_endscreen_layout()
        self.assertEqual(design.total_duration_sec, 20.0)
        self.assertEqual(len(design.slots), 3)
        types = [s.element_type for s in design.slots]
        self.assertIn("subscribe_button", types)
        self.assertIn("next_video", types)

    def test_audio_monotony_breaker(self):
        cues = AudioMonotonyBreaker.audit_and_schedule_variations(self.plan)
        # Total duration is 17s (> 11s), should produce a breaker cue!
        self.assertGreaterEqual(len(cues), 1)
        self.assertEqual(cues[0].breaker_type, MonotonyBreakerType.STRING_SWELL)

    def test_b_roll_audio_leveler(self):
        specs = BRollAudioLeveler.calculate_leveling_chain(self.plan)
        self.assertEqual(len(specs), 3)
        self.assertEqual(specs[0].target_bed_volume_db, -24.0)
        self.assertIn("volume=", specs[0].ffmpeg_volume_filter)

    def test_multilingual_subtitles(self):
        bundle = MultilingualSubtitlesBundle.generate_bundle(self.plan)
        self.assertEqual(len(bundle), 10)
        lang_codes = [p.language_code for p in bundle]
        self.assertIn("en", lang_codes)
        self.assertIn("es", lang_codes)
        self.assertIn("WEBVTT", bundle[0].vtt_content)

    def test_auto_summarizer_cut(self):
        summary = AutoSummarizerCut.condense_project(self.plan, target_max_duration=12.0)
        self.assertLessEqual(summary.summary_duration, self.plan.total_duration())
        self.assertGreater(len(summary.selected_scene_orders), 0)

    def test_copyright_shield(self):
        cert = CopyrightSafeShield.generate_clearance_certificate(self.plan)
        self.assertTrue(cert.is_fully_cleared)
        self.assertIn("CERT-DRIFT", cert.certificate_id)
        self.assertEqual(len(cert.records), 1)

    def test_seo_tag_architect(self):
        kit = SeoTagArchitect.generate_seo_kit(self.plan)
        self.assertIn("História dos Oceanos", kit.optimized_title)
        self.assertIn("oceanos", kit.tags_comma_string.lower())
        self.assertLessEqual(kit.tags_character_count, 500)

    def test_genre_morphing_engine(self):
        res = GenreMorphingEngine.morph_genre(self.plan, MusicGenre.LOFI_CHILL)
        self.assertEqual(res.target_genre, MusicGenre.LOFI_CHILL)
        self.assertEqual(res.base_tempo_bpm, 84)
        self.assertIn("Rhodes", res.stem_layers[0])

    def test_battery_saver_engine(self):
        prof = BatterySaverEngine.get_power_profile(PowerState.BATTERY_DISCHARGING)
        self.assertEqual(prof.preview_framerate_fps, 24)
        self.assertFalse(prof.realtime_color_lut_enabled)

if __name__ == "__main__":
    unittest.main()
