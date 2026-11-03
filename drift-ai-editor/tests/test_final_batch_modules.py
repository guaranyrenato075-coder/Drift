"""
Unit tests for the final batch of 10 cinema & studio-grade modules:
ParallaxProjectionEngine, JLCutDirector, VirtualRelightingEngine,
ScriptConcisenessAuditor, QuoteCardPopup, DynamicSpeechPacer,
AestheticThemeDirector, DriftBundlePackager, VisualImpactPunch,
ReadingEaseAnalyzer.
"""
import os
import shutil
import tempfile
import unittest

from models.scene_plan import ProjectPlan, Scene
from editing.parallax_2_5d_projection import ParallaxProjectionEngine, ParallaxCameraMove
from editing.j_l_cut_builder import JLCutDirector, SplitCutType
from editing.virtual_relighting import VirtualRelightingEngine, LightingStyle
from analysis.script_conciseness_auditor import ScriptConcisenessAuditor
from editing.quote_card_popup import QuoteCardPopup
from voice.dynamic_speech_pacer import DynamicSpeechPacer, PacingStatus
from pipeline.aesthetic_theme_presets import AestheticThemeDirector, AestheticTheme
from pipeline.drift_bundle_packager import DriftBundlePackager
from editing.visual_impact_punch import VisualImpactPunch, ImpactType
from analysis.reading_ease_analyzer import ReadingEaseAnalyzer

class TestFinalBatchModules(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.plan = ProjectPlan(title="Jornada Estelar")
        s1 = Scene(order=1, narration_text="Tipo assim, as estrelas no céu brilham basicamente sem parar.", visual_description="Céu estrelado", duration=4.0)
        s2 = Scene(order=2, narration_text="Astrônomos mapearam novas galáxias distantes.", visual_description="Telescópio espacial", duration=5.0)
        s3 = Scene(order=3, narration_text="A física quântica nos ensina sobre a origem do tempo.", visual_description="Constelações", duration=5.0)
        self.plan.scenes = [s1, s2, s3]
        self.plan.reindex_scenes()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_parallax_projection_engine(self):
        spec = ParallaxProjectionEngine.generate_parallax_spec(ParallaxCameraMove.SLOW_DOLLY_IN, duration_sec=5.0)
        self.assertEqual(spec.duration_sec, 5.0)
        self.assertEqual(spec.move_type, ParallaxCameraMove.SLOW_DOLLY_IN)
        self.assertIn("zoompan=", spec.ffmpeg_complex_filter)

    def test_j_l_cut_builder(self):
        transitions = JLCutDirector.schedule_split_cuts(self.plan)
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0].split_type, SplitCutType.J_CUT)
        self.assertEqual(transitions[0].audio_lead_offset_sec, 0.5)

    def test_virtual_relighting(self):
        spec = VirtualRelightingEngine.create_lighting_filter(LightingStyle.CLASSIC_PORTRAIT)
        self.assertEqual(spec.style, LightingStyle.CLASSIC_PORTRAIT)
        self.assertIn("curves=", spec.ffmpeg_filter)

    def test_script_conciseness_auditor(self):
        report = ScriptConcisenessAuditor.audit_project(self.plan)
        self.assertGreater(report.total_fillers_detected, 0)
        self.assertIn("Tipo assim", [a.filler_match for a in report.alerts])
        self.assertGreater(report.estimated_seconds_saved, 0.0)

    def test_quote_card_popup(self):
        spec = QuoteCardPopup.create_quote_card(
            quote_text="O cosmos está dentro de nós.",
            author="Carl Sagan",
            source_work="Cosmos",
            start_sec=1.0,
            duration_sec=3.5,
            theme="parchment_gold"
        )
        self.assertEqual(spec.author, "Carl Sagan")
        self.assertIn("Carl Sagan (Cosmos)", spec.ffmpeg_complex_filter)
        self.assertIn("drawbox=", spec.ffmpeg_complex_filter)

    def test_dynamic_speech_pacer(self):
        summary = DynamicSpeechPacer.audit_project(self.plan)
        self.assertEqual(len(summary.scenes), 3)
        self.assertGreater(summary.average_wpm, 0.0)
        self.assertIn(summary.scenes[0].status, [PacingStatus.OPTIMAL, PacingStatus.TOO_SLOW, PacingStatus.TOO_FAST])

    def test_aesthetic_theme_presets(self):
        spec = AestheticThemeDirector.apply_theme_to_project(self.plan, AestheticTheme.CYBERPUNK_NEON)
        self.assertEqual(spec.theme, AestheticTheme.CYBERPUNK_NEON)
        self.assertEqual(self.plan.scenes[0].transition, "glitch_cut")

    def test_drift_bundle_packager(self):
        bundle_path = os.path.join(self.tmp_dir, "project.driftbundle")
        manifest = DriftBundlePackager.export_bundle(self.plan, bundle_path)
        self.assertTrue(os.path.isfile(bundle_path))
        self.assertEqual(manifest.total_scenes, 3)

        inspected = DriftBundlePackager.inspect_bundle(bundle_path)
        self.assertEqual(inspected.project_title, "Jornada Estelar")

        extract_dir = os.path.join(self.tmp_dir, "unpacked")
        restored = DriftBundlePackager.extract_bundle(bundle_path, extract_dir)
        self.assertEqual(len(restored.scenes), 3)
        self.assertEqual(restored.scenes[0].visual_description, "Céu estrelado")

    def test_visual_impact_punch(self):
        zoom = VisualImpactPunch.create_snap_zoom(2.5, duration_frames=12, scale_factor=1.14)
        self.assertEqual(zoom.impact_type, ImpactType.SNAP_ZOOM)
        self.assertIn("zoompan=", zoom.ffmpeg_video_filter)

        flash = VisualImpactPunch.create_flash_frame(1.0)
        self.assertEqual(flash.impact_type, ImpactType.FLASH_FRAME)
        self.assertIn("eq=brightness=", flash.ffmpeg_video_filter)

    def test_reading_ease_analyzer(self):
        report = ReadingEaseAnalyzer.analyze_project(self.plan)
        self.assertGreater(report.total_words, 0)
        self.assertGreater(report.flesch_reading_ease, 0.0)
        self.assertGreater(report.flesch_kincaid_grade, 0.0)
        self.assertIsNotNone(report.reading_difficulty_label)

if __name__ == "__main__":
    unittest.main()
