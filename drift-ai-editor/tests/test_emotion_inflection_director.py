"""
Unit tests for AIVoiceEmotionInflectionDirector in CutWire Drift AI.
Verifies scene mood evaluation and prosody SSML parameter generation.
"""
import unittest
from voice.emotion_inflection_director import AIVoiceEmotionInflectionDirector
from models.scene_plan import ProjectPlan, Scene

class TestEmotionInflectionDirector(unittest.TestCase):

    def test_evaluate_scene_mood_intro_and_conclusion(self):
        s1 = Scene(order=1, narration_text="Introdução enigmática.")
        s2 = Scene(order=2, narration_text="Um perigo e explosão iminente!")
        s3 = Scene(order=3, narration_text="E assim concluímos esta jornada solene.")

        mood1 = AIVoiceEmotionInflectionDirector.evaluate_scene_mood(s1, total_scenes=3)
        mood2 = AIVoiceEmotionInflectionDirector.evaluate_scene_mood(s2, total_scenes=3)
        mood3 = AIVoiceEmotionInflectionDirector.evaluate_scene_mood(s3, total_scenes=3)

        self.assertEqual(mood1, "misterioso")
        self.assertEqual(mood2, "urgente_climax")
        self.assertEqual(mood3, "solene_conclusao")

    def test_calculate_scene_inflection(self):
        s = Scene(order=2, narration_text="Cuidado com a revelação!")
        inf = AIVoiceEmotionInflectionDirector.calculate_scene_inflection(s, "urgente_climax")

        self.assertEqual(inf.narrative_mood, "urgente_climax")
        self.assertEqual(inf.speed_factor, 1.08)
        self.assertEqual(inf.pitch_adjustment_hz, "+8Hz")
        self.assertIn('<prosody rate="+8%"', inf.ssml_prosody_snippet)

    def test_direct_project_voice_inflections(self):
        plan = ProjectPlan(title="Projeto Voz Emocional")
        plan.scenes = [
            Scene(order=1, narration_text="Intro."),
            Scene(order=2, narration_text="Clímax perigoso!"),
            Scene(order=3, narration_text="Fim.")
        ]

        res = AIVoiceEmotionInflectionDirector.direct_project_voice_inflections(plan)
        self.assertEqual(res["total_scenes_directed"], 3)
        self.assertEqual(len(res["inflections"]), 3)

if __name__ == '__main__':
    unittest.main()
