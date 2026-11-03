"""
Unit tests for next-generation features:
RetentionPredictor, PunctuationSfxDirector, SmartActionReframe,
GenerativeAiFallback, AnimatedMapGenerator, KineticInfographicsEngine,
LongToShortsExtractor, ThumbnailStudio, KineticCaptionsEngine,
LufsAudioMasterer, NoiseSuppressor, TimelineChatCopilot.
"""
import unittest
from models.scene_plan import ProjectPlan, Scene
from analysis.retention_predictor import RetentionPredictor
from audio.punctuation_sfx import PunctuationSfxDirector, SfxType
from editing.smart_action_reframe import SmartActionReframe
from extensions.generative_fallback import GenerativeAiFallback
from editing.animated_map_generator import AnimatedMapGenerator
from editing.kinetic_infographics import KineticInfographicsEngine, InfographicType
from pipeline.long_to_shorts_extractor import LongToShortsExtractor
from pipeline.thumbnail_studio import ThumbnailStudio, ThumbnailStrategy
from editing.kinetic_captions import KineticCaptionsEngine
from audio.lufs_mastering import LufsAudioMasterer, TargetPlatform
from voice.noise_suppressor import NoiseSuppressor
from director.timeline_chat_copilot import TimelineChatCopilot, CopilotIntent

class TestNeuroRetentionAndCopilot(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(title="Projeto Piloto de Teste")
        self.plan.scenes = [
            Scene(order=1, narration_text="Bem-vindos a esta jornada incrível pelo cosmos.", duration=3.0),
            Scene(order=2, narration_text="Mas um perigo secreto e chocante mudou a história para sempre.", duration=4.0),
            Scene(order=3, narration_text="O crescimento da tecnologia atingiu 42% em 2024.", duration=5.0),
            Scene(order=4, narration_text="As tropas marcharam de Roma para Berlim sem hesitar.", duration=7.5),
            Scene(order=5, narration_text="E a verdade final é que nunca mais fomos os mesmos.", duration=4.0)
        ]
        self.plan.reindex_scenes()

    def test_retention_predictor(self):
        forecast = RetentionPredictor.forecast_project(self.plan)
        self.assertGreater(forecast.overall_retention_score, 0)
        self.assertGreater(len(forecast.pacing_graph), 3)
        # Scene 4 is 7.5s (over 6.5s limit), should create a risk zone
        self.assertGreater(len(forecast.risk_zones), 0)
        self.assertIn("Scene #4", forecast.risk_zones[0].primary_cause)

    def test_punctuation_sfx_director(self):
        cues = PunctuationSfxDirector.schedule_project_sfx(self.plan)
        self.assertGreater(len(cues), 2)
        # Verify whoosh transitions and sub-hits
        types = [c.sfx_type for c in cues]
        self.assertIn(SfxType.WHOOSH_TRANSITION, types)
        self.assertIn(SfxType.SUB_HIT_IMPACT, types)

    def test_smart_action_reframe(self):
        plan = SmartActionReframe.compute_crop_plan("clip_1", duration=4.0, detected_action_points=[(0.0, 0.4), (2.0, 0.6)])
        self.assertEqual(plan.target_resolution, (607, 1080))
        self.assertEqual(len(plan.keyframes), 2)
        self.assertIn("crop=", plan.ffmpeg_crop_filter)

    def test_generative_fallback(self):
        req = GenerativeAiFallback.craft_generation_request(1, "medieval philosopher on Mars", style="cinematic")
        self.assertIn("medieval philosopher", req.positive_prompt)
        self.assertIn("cinematic lighting", req.positive_prompt)
        res = GenerativeAiFallback.simulate_local_render(req)
        self.assertTrue(res.success)
        self.assertIn("gen_scene_01.png", res.image_path)

    def test_animated_map_generator(self):
        route = AnimatedMapGenerator.detect_and_generate_route(4, "As tropas marcharam de Roma para Berlim sem hesitar.")
        self.assertIsNotNone(route)
        self.assertEqual(route.origin.city_or_place, "Roma")
        self.assertEqual(route.destination.city_or_place, "Berlim")
        self.assertIn("M ", route.svg_route_path)

    def test_kinetic_infographics(self):
        overlay = KineticInfographicsEngine.scan_scene_data(3, "O crescimento da tecnologia atingiu 42% em 2024.", start_time=12.0, duration=5.0)
        self.assertIsNotNone(overlay)
        self.assertEqual(overlay.infographic_type, InfographicType.PERCENTAGE_COUNTER)
        self.assertEqual(overlay.target_value, 42.0)

    def test_long_to_shorts_extractor(self):
        shorts = LongToShortsExtractor.extract_shorts(self.plan, min_duration=5.0, max_duration=25.0)
        self.assertGreater(len(shorts), 0)
        self.assertIn("Viral Short", shorts[0].title)
        self.assertGreater(shorts[0].virality_score, 50)

    def test_thumbnail_studio(self):
        variants = ThumbnailStudio.generate_ab_variants(self.plan)
        self.assertEqual(len(variants), 3)
        self.assertEqual(variants[0].strategy, ThumbnailStrategy.CURIOSITY_GAP)
        self.assertEqual(variants[1].strategy, ThumbnailStrategy.SHOCK_URGENCY)
        self.assertEqual(variants[2].strategy, ThumbnailStrategy.AUTHORITY_DATA)

    def test_kinetic_captions(self):
        block = KineticCaptionsEngine.generate_kinetic_block(2, "O perigo do segredo revelado com fogo", start_time=0.0, duration=3.0)
        self.assertEqual(len(block.word_cues), 7)
        # Check emoji trigger for "fogo" -> 🔥
        self.assertEqual(block.word_cues[-1].attached_emoji, "🔥")
        self.assertIn("fscx115", block.ass_dialogue_line)

    def test_lufs_mastering(self):
        recipe = LufsAudioMasterer.get_mastering_recipe(TargetPlatform.YOUTUBE)
        self.assertEqual(recipe.preset.target_lufs, -14.0)
        self.assertIn("loudnorm=I=-14.0", recipe.ffmpeg_loudnorm_filter)

    def test_noise_suppressor(self):
        profile = NoiseSuppressor.create_vocal_chain(has_aircon_hum=True, has_room_echo=True)
        self.assertIn("highpass=f=80", profile.ffmpeg_audio_filter)
        self.assertIn("deesser=", profile.ffmpeg_audio_filter)

    def test_timeline_chat_copilot(self):
        # 1. Pacing command
        res_pacing = TimelineChatCopilot.execute_command(self.plan, "Deixe a intro mais rápida")
        self.assertTrue(res_pacing.success)
        self.assertEqual(res_pacing.intent, CopilotIntent.ACCELERATE_PACING)

        # 2. Duration scale command
        res_fit = TimelineChatCopilot.execute_command(self.plan, "Faça o vídeo durar 20 segundos")
        self.assertTrue(res_fit.success)
        self.assertEqual(res_fit.intent, CopilotIntent.FIT_EXACT_DURATION)
        self.assertAlmostEqual(self.plan.total_duration(), 20.0, places=1)

if __name__ == "__main__":
    unittest.main()

