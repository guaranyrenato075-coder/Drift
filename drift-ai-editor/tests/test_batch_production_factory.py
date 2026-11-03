import unittest
import os
import shutil
from pathlib import Path
from pipeline.batch_production_factory import BatchProductionFactory, BatchVideoJob, BatchFactoryState
from storage.repository import ProjectRepository

class TestBatchProductionFactory(unittest.TestCase):

    def setUp(self):
        self.test_root = "d:/CUTWIREDRIFT/test_batch_factory_out"
        self.repo = ProjectRepository()
        self.factory = BatchProductionFactory(output_root=self.test_root, repo=self.repo)

    def tearDown(self):
        if Path(self.test_root).exists():
            shutil.rmtree(self.test_root, ignore_errors=True)

    def test_create_batch_from_topics(self):
        topics = [
            "A Arte da Disciplina Diária",
            "Como Vencer a Procrastinação",
            "O Poder do Hábito Atômico"
        ]
        jobs = self.factory.create_batch_from_topics(topics)
        self.assertEqual(len(jobs), 3)
        self.assertEqual(jobs[0].topic, "A Arte da Disciplina Diária")
        self.assertEqual(jobs[0].status, "queued")
        self.assertEqual(jobs[0].progress_pct, 0)

        state = self.factory.get_state()
        self.assertEqual(state.total_jobs, 3)
        self.assertEqual(state.completed_jobs, 0)
        self.assertEqual(state.overall_progress_pct, 0.0)

    def test_process_single_video_end_to_end(self):
        topics = ["Foco Inabalável"]
        self.factory.create_batch_from_topics(topics)
        job = self.factory.jobs[0]

        # Executa processamento do vídeo
        self.factory._process_single_video(job)

        self.assertEqual(job.status, "ready")
        self.assertEqual(job.progress_pct, 100)
        self.assertIsNotNone(job.project_id)
        self.assertIsNotNone(job.output_dir)
        self.assertGreater(job.total_scenes, 0)
        self.assertGreater(job.duration_sec, 0.0)
        self.assertTrue(job.copyright_monetizable)

        out_dir = Path(job.output_dir)
        self.assertTrue(out_dir.exists())

        # Verifica arquivos gerados no pacote completo
        self.assertTrue((out_dir / "legendas_karaoke.ass").exists())
        self.assertTrue((out_dir / "publicacao_youtube_e_tiktok.txt").exists())
        self.assertTrue((out_dir / "thumbnails_estrategias.json").exists())
        self.assertTrue((out_dir / "render_manifest.json").exists())
        self.assertTrue((out_dir / "audio").exists())

        # Verifica se o plano foi salvo no repositório SQLite
        saved_plan = self.repo.get(job.project_id)
        self.assertIsNotNone(saved_plan)
        self.assertEqual(saved_plan.project_id, job.project_id)

    def test_stop_batch(self):
        self.factory.create_batch_from_topics(["Tema 1", "Tema 2"])
        self.factory.is_running = True
        self.factory.stop_batch()
        self.assertFalse(self.factory.is_running)

if __name__ == "__main__":
    unittest.main()

