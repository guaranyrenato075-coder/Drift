"""
Unit tests for CutWire Drift AI Advanced Production Suite:
1. MultilingualAudioPackager (Multi-audio track multiplexing)
2. SmartSilenceBreathStripper (Audio silence detection & pacing compression)
3. MotionInfographicsGenerator (Numeric & percentage visual motion counter filters)
4. BRollGapFiller (Archival footage allocation from NASA/Smithsonian/Met)
"""
import unittest
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scene_plan import Scene, SceneState
from pipeline.multilingual_audio_packager import MultilingualAudioPackager, MultiAudioExportSpec
from audio.smart_silence_breath_stripper import SmartSilenceBreathStripper, AudioTighteningReport
from editing.motion_infographics_generator import MotionInfographicsGenerator, InfographicsPlan
from media.b_roll_gap_filler import BRollGapFiller, BRollPlan

class TestAdvancedProductionSuite(unittest.TestCase):

    def test_multilingual_audio_packager(self):
        tracks = [
            {"language": "pt", "file_path": "d:/renders/pt.mp3", "title": "Português", "is_default": True},
            {"language": "en", "file_path": "d:/renders/en.mp3", "title": "English"},
            {"language": "es", "file_path": "d:/renders/es.mp3", "title": "Español"}
        ]
        spec = MultilingualAudioPackager.create_multilingual_spec(
            project_id="global_doc_101",
            video_path="d:/renders/video_clean.mp4",
            audio_tracks=tracks
        )
        self.assertEqual(len(spec.tracks), 3)
        self.assertEqual(spec.tracks[0].language_code, "por")
        self.assertEqual(spec.tracks[1].language_code, "eng")
        self.assertEqual(spec.tracks[2].language_code, "spa")
        
        # Validação dos mapeamentos de faixas e metadados FFmpeg
        cmd = " ".join(spec.ffmpeg_command_args)
        self.assertIn("-map 0:v:0", cmd)
        self.assertIn("-map 1:a:0", cmd)
        self.assertIn("-map 2:a:0", cmd)
        self.assertIn("-map 3:a:0", cmd)
        self.assertIn("-metadata:s:a:0 language=por", cmd)
        self.assertIn("-metadata:s:a:1 language=eng", cmd)
        self.assertIn("-metadata:s:a:2 language=spa", cmd)

    def test_smart_silence_breath_stripper(self):
        # Narração de 600 segundos (10 minutos)
        report = SmartSilenceBreathStripper.analyze_and_generate_filter(
            estimated_duration_sec=600.0,
            silence_threshold_db=-38.0,
            min_silence_duration_sec=0.35
        )
        self.assertEqual(report.original_duration_sec, 600.0)
        self.assertLess(report.tightened_duration_sec, 600.0)
        self.assertGreater(report.seconds_saved, 10.0)
        self.assertGreater(report.percentage_tightened, 2.0)
        self.assertIn("silenceremove=", report.ffmpeg_filter)
        self.assertIn("-38.0dB", report.ffmpeg_filter)

        # Testa construção de comando completo
        cmd = SmartSilenceBreathStripper.build_tighten_command("input.mp3", "output.mp3")
        self.assertIn("-af", cmd)
        self.assertIn("-c:a", cmd)

    def test_motion_infographics_generator(self):
        scenes = [
            Scene(order=1, narration_text="Em 1969 o ser humano realizou o primeiro pouso na lua.", duration=6.0),
            Scene(order=2, narration_text="Mais de 500 milhões de pessoas acompanharam a transmissão ao vivo.", duration=7.0),
            Scene(order=3, narration_text="A precisão dos instrumentos foi estimada em 99.8% de eficácia.", duration=5.0)
        ]

        plan = MotionInfographicsGenerator.scan_project_scenes(scenes)
        self.assertEqual(plan.total_elements, 3)

        types = [item.data_type for item in plan.items]
        self.assertIn("historical_year", types)
        self.assertIn("large_number", types)
        self.assertIn("percentage", types)

        # Validação do drawtext filter gerado
        year_item = next(it for it in plan.items if it.data_type == "historical_year")
        self.assertEqual(year_item.target_value, 1969.0)
        self.assertIn("drawtext=text=", year_item.ffmpeg_drawtext_filter)

        pct_item = next(it for it in plan.items if it.data_type == "percentage")
        self.assertEqual(pct_item.target_value, 99.8)
        self.assertEqual(pct_item.unit_suffix, "%")

    def test_b_roll_gap_filler(self):
        scenes = [
            Scene(order=1, narration_text="A exploração do espaço revelou segredos incríveis sobre cada galáxia.", duration=8.0),
            Scene(order=2, narration_text="Na Roma antiga os generais comandavam grandes exércitos.", duration=7.0),
            Scene(order=3, narration_text="Cena rápida sem menção de arquivos.", duration=2.0) # <4s deve ser ignorada
        ]

        broll_plan = BRollGapFiller.generate_plan(scenes)
        self.assertEqual(broll_plan.total_insertions, 2)
        
        # Validação dos provedores atribuídos
        space_broll = broll_plan.insertions[0]
        self.assertEqual(space_broll.target_scene_order, 1)
        self.assertEqual(space_broll.recommended_provider, "nasa")

        rome_broll = broll_plan.insertions[1]
        self.assertEqual(rome_broll.target_scene_order, 2)
        self.assertEqual(rome_broll.recommended_provider, "met_museum")

if __name__ == "__main__":
    unittest.main()

