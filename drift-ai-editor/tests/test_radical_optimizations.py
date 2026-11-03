import unittest
import os
from pathlib import Path
from models.scene_plan import ProjectPlan, ProjectConfig, Scene, MediaCandidate
from core.ram_disk_buffer import RamDiskBufferManager, RamDiskStats
from storage.media_deduplicator import MediaDeduplicator, DeduplicationStats
from media.speculative_prefetcher import SpeculativeMediaPrefetcher, PrefetchBatchSummary
from editing.adaptive_crf_encoder import AdaptiveCrfEncoder, SceneComplexity, AdaptiveEncodingManifest

class TestRadicalOptimizations(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(
            project_id="test_opt_project",
            title="A Máquina Eficiente",
            config=ProjectConfig(aspect_ratio="16:9", media_type="video"),
            scenes=[
                Scene(
                    order=1,
                    visual_description="Uma pessoa sentada em meditação calma em frente ao lago silencioso.",
                    english_keywords=["calm", "meditation", "lake"],
                    duration=5.0
                ),
                Scene(
                    order=2,
                    visual_description="Carros de corrida em alta velocidade numa pista com muita ação e fumaça.",
                    english_keywords=["car", "racing", "speed", "action"],
                    duration=6.0
                ),
                Scene(
                    order=3,
                    visual_description="Cidade urbana ao entardecer com tráfego normal e pedestres caminhando.",
                    english_keywords=["city", "walking", "sunset"],
                    duration=4.5
                )
            ]
        )

    def test_ram_disk_buffer(self):
        ram_mgr = RamDiskBufferManager(budget_mb=1024.0, cache_dir="d:/CUTWIREDRIFT/test_ram_cache")
        try:
            # Cria arquivo simulado
            dummy_file = "d:/CUTWIREDRIFT/test_ram_cache/dummy_src.mp4"
            Path(dummy_file).parent.mkdir(parents=True, exist_ok=True)
            with open(dummy_file, "wb") as f:
                f.write(b"0" * 1024 * 50) # 50 KB

            proxy_path = ram_mgr.cache_scene_proxy(scene_order=1, source_path=dummy_file, resolution="720p")
            self.assertTrue(os.path.exists(proxy_path))
            self.assertIn("scene_001_proxy", proxy_path)

            stats = ram_mgr.get_stats()
            self.assertIsInstance(stats, RamDiskStats)
            self.assertEqual(stats.cached_assets_count, 1)
            self.assertGreater(stats.used_mb, 0.0)
            self.assertGreaterEqual(stats.read_speedup_factor, 50.0)
        finally:
            ram_mgr.clear()
            if os.path.exists("d:/CUTWIREDRIFT/test_ram_cache"):
                try:
                    os.rmdir("d:/CUTWIREDRIFT/test_ram_cache")
                except Exception:
                    pass

    def test_media_deduplicator(self):
        dedup = MediaDeduplicator(master_store_dir="d:/CUTWIREDRIFT/test_cas_store")
        temp_dir = Path("d:/CUTWIREDRIFT/test_cas_temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            # Cria 2 arquivos com o MESMO conteúdo em locais temporários diferentes
            src1 = temp_dir / "sound_effect_a.wav"
            src2 = temp_dir / "sound_effect_b.wav"
            content = b"RIFF_DRIFT_IDENTICAL_AUDIO_DATA_FOR_DEDUPLICATION_TEST"
            with open(src1, "wb") as f: f.write(content)
            with open(src2, "wb") as f: f.write(content)

            dest1 = temp_dir / "project_1/sfx.wav"
            dest2 = temp_dir / "project_2/sfx.wav"

            p1, is_dedup1 = dedup.deduplicate_and_link(str(src1), str(dest1))
            self.assertFalse(is_dedup1) # Primeira vez: grava no CAS mestre

            p2, is_dedup2 = dedup.deduplicate_and_link(str(src2), str(dest2))
            self.assertTrue(is_dedup2) # Segunda vez: detecta SHA idêntico e cria Hardlink!

            stats = dedup.get_stats()
            self.assertIsInstance(stats, DeduplicationStats)
            self.assertEqual(stats.total_unique_assets, 1)
            self.assertEqual(stats.total_referenced_links, 2)
            self.assertGreaterEqual(stats.savings_percentage, 40.0)
        finally:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            if Path("d:/CUTWIREDRIFT/test_cas_store").exists():
                shutil.rmtree("d:/CUTWIREDRIFT/test_cas_store", ignore_errors=True)

    def test_speculative_prefetcher(self):
        prefetcher = SpeculativeMediaPrefetcher(max_workers=2)
        # Mock do plano com candidatos já com local path simulado
        plan = ProjectPlan(
            project_id="prefetch_test",
            title="Teste Prefetch",
            config=ProjectConfig(),
            scenes=[
                Scene(
                    order=1,
                    selected_media=MediaCandidate(
                        candidate_id="c1",
                        platform="pexels",
                        local_cached_path="d:/CUTWIREDRIFT/dummy.mp4"
                    )
                )
            ]
        )
        summary = prefetcher.prefetch_plan_candidates_sync(plan)
        self.assertIsInstance(summary, PrefetchBatchSummary)
        self.assertEqual(summary.total_scenes_queued, 1)

    def test_adaptive_crf_encoder(self):
        # Cena 1 é calma (LOW_STATIC)
        comp_s1 = AdaptiveCrfEncoder.evaluate_scene_complexity(self.plan.scenes[0])
        self.assertEqual(comp_s1, SceneComplexity.LOW_STATIC)

        # Cena 2 é de ação (HIGH_DYNAMIC)
        comp_s2 = AdaptiveCrfEncoder.evaluate_scene_complexity(self.plan.scenes[1])
        self.assertEqual(comp_s2, SceneComplexity.HIGH_DYNAMIC)

        manifest = AdaptiveCrfEncoder.generate_encoding_manifest(self.plan, is_gpu_nvenc=False)
        self.assertIsInstance(manifest, AdaptiveEncodingManifest)
        self.assertEqual(manifest.total_scenes, 3)
        self.assertGreater(manifest.estimated_bandwidth_savings_pct, 20.0)
        self.assertGreaterEqual(manifest.average_crf, 20.0)

        # Verifica receita da cena estática vs cena de ação
        recipe_static = manifest.recipes[0]
        recipe_action = manifest.recipes[1]
        self.assertGreater(recipe_static.target_crf, recipe_action.target_crf)
        self.assertLess(recipe_static.max_bitrate_kbps, recipe_action.max_bitrate_kbps)

if __name__ == "__main__":
    unittest.main()

