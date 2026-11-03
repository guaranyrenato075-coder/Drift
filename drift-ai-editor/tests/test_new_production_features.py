import unittest
from models.scene_plan import ProjectPlan, ProjectConfig, Scene, MediaCandidate
from media.copyright_analyzer import CopyrightAnalyzer, CopyrightStatus
from audio.auto_ducking_soundtrack import AutoDuckingSoundtrackMixer
from pipeline.hybrid_multiformat_producer import HybridMultiFormatProducer, FramingMode
from pipeline.thumbnail_studio import ThumbnailStudio
from pipeline.publication_seo_kit import PublicationSeoKitGenerator

class TestNewProductionFeatures(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(
            project_id="test_proj_advanced",
            title="A Mente Focada",
            config=ProjectConfig(aspect_ratio="16:9", media_type="video"),
            scenes=[
                Scene(
                    order=1,
                    narration_text="A disciplina diária constrói o sucesso que você busca.",
                    duration=5.0,
                    selected_media=MediaCandidate(
                        candidate_id="safe_cand_1",
                        platform="pexels",
                        title="Homem correndo no parque",
                        license="Pexels License"
                    ),
                    candidates=[
                        MediaCandidate(
                            candidate_id="safe_cand_1",
                            platform="pexels",
                            title="Homem correndo no parque",
                            license="Pexels License"
                        )
                    ]
                ),
                Scene(
                    order=2,
                    narration_text="Mas distrações roubam sua atenção a todo momento.",
                    duration=6.0,
                    selected_media=MediaCandidate(
                        candidate_id="risky_cand_2",
                        platform="flickr",
                        title="Foto Comercial Proibida",
                        license="CC-BY-NC-4.0"
                    ),
                    candidates=[
                        MediaCandidate(
                            candidate_id="cand_clean_backup",
                            platform="pixabay",
                            title="Luzes da cidade à noite",
                            license="Pixabay Content License"
                        )
                    ]
                ),
                Scene(
                    order=3,
                    narration_text="Recupere o controle da sua mente hoje mesmo.",
                    duration=4.5,
                    selected_media=MediaCandidate(
                        candidate_id="safe_cand_3",
                        platform="unsplash",
                        title="Pessoa meditando",
                        license="Unsplash License"
                    )
                )
            ]
        )

    def test_auto_remediate_copyright(self):
        # Cena 2 tinha uma mídia de risco (CC-NC). O remediator deve substituí-la.
        audit_before = CopyrightAnalyzer.audit_timeline_copyright(self.plan)
        self.assertEqual(audit_before.restricted_scenes_count, 1)
        self.assertFalse(audit_before.is_safe_for_monetization)

        # Executa remediação automática
        remediate_res = CopyrightAnalyzer.auto_remediate_project(self.plan)
        self.assertTrue(remediate_res["success"])
        self.assertEqual(remediate_res["remediated_count"], 1)

        # Verifica nova auditoria
        audit_after = CopyrightAnalyzer.audit_timeline_copyright(self.plan)
        self.assertEqual(audit_after.restricted_scenes_count, 0)
        self.assertTrue(audit_after.is_safe_for_monetization)
        self.assertGreaterEqual(audit_after.overall_copyright_score, 80)

    def test_auto_ducking_soundtrack(self):
        mix_plan = AutoDuckingSoundtrackMixer.generate_mix_plan(self.plan, music_profile="ambient_cinematic", base_bpm=120)
        self.assertEqual(mix_plan.project_id, "test_proj_advanced")
        self.assertGreater(mix_plan.total_duration, 0.0)
        self.assertEqual(mix_plan.idle_volume_db, -6.0)
        self.assertEqual(mix_plan.ducked_volume_db, -22.0)
        self.assertGreater(len(mix_plan.keyframes), 0)
        self.assertGreater(len(mix_plan.beat_grid), 0)
        self.assertEqual(len(mix_plan.aligned_transitions), 3)

        # Verifica se há keyframes com ação de ducking durante a fala
        duck_actions = [k.action for k in mix_plan.keyframes]
        self.assertIn("duck_attack", duck_actions)
        self.assertIn("duck_release", duck_actions)

    def test_hybrid_multiformat_producer(self):
        hybrid_report = HybridMultiFormatProducer.generate_hybrid_specs(
            self.plan,
            framing_mode=FramingMode.BLURRED_PILLARBOX
        )
        self.assertEqual(hybrid_report.total_formats, 2)
        
        formats_dict = {f.format_name: f for f in hybrid_report.formats}
        self.assertIn("youtube_master_16x9", formats_dict)
        self.assertIn("tiktok_shorts_9x16", formats_dict)

        shorts_spec = formats_dict["tiktok_shorts_9x16"]
        self.assertEqual(shorts_spec.aspect_ratio, "9:16")
        self.assertEqual(shorts_spec.resolution, "1080x1920")
        self.assertIsNotNone(shorts_spec.safe_zone)
        self.assertEqual(shorts_spec.safe_zone.bottom_margin_pct, 22.0)
        self.assertIn("boxblur", shorts_spec.ffmpeg_filter_complex)

    def test_thumbnail_studio_with_heatmap(self):
        variants = ThumbnailStudio.generate_ab_variants(self.plan)
        self.assertEqual(len(variants), 3)

        var_a = variants[0]
        self.assertEqual(var_a.variant_id, "thumb_var_a")
        self.assertGreaterEqual(var_a.predicted_ctr_score, 60)
        self.assertIsNotNone(var_a.primary_focal_point)
        # Variante C sem rosto humano deve ter recomendação de melhoria de CTR
        var_c = variants[2]
        self.assertGreater(len(var_c.heatmap_recommendations), 0)

    def test_publication_seo_kit(self):
        kit = PublicationSeoKitGenerator.generate_complete_kit(self.plan)
        self.assertEqual(kit.project_title, "A Mente Focada")
        self.assertEqual(len(kit.magnetic_titles), 5)
        self.assertIn("00:00", kit.youtube_chapters)
        self.assertGreater(len(kit.search_tags_comma_separated), 10)
        self.assertGreater(len(kit.trending_hashtags), 0)
        self.assertIn("CAPÍTULOS E TIMESTAMPS", kit.complete_youtube_description)
        self.assertIn("DECLARAÇÃO DE DIREITOS AUTORAIS", kit.complete_youtube_description)

if __name__ == "__main__":
    unittest.main()
