import unittest
import os
from core.render_crash_recovery_guard import AutoRenderCrashRecoveryGuard


class TestRenderCrashRecoveryGuard(unittest.TestCase):
    def setUp(self):
        self.project_id = "test_proj_recovery_123"
        AutoRenderCrashRecoveryGuard.clear_checkpoint(self.project_id)

    def tearDown(self):
        AutoRenderCrashRecoveryGuard.clear_checkpoint(self.project_id)

    def test_checkpoint_lifecycle(self):
        # 1. Sem checkpoint
        check1 = AutoRenderCrashRecoveryGuard.check_resumable_render(self.project_id)
        self.assertFalse(check1["has_resumable_checkpoint"])

        # 2. Salva checkpoint no meio do render (cena 2 de 5)
        saved = AutoRenderCrashRecoveryGuard.save_checkpoint(
            project_id=self.project_id,
            scene_index=2,
            total_scenes=5,
            completed_files=["chunk_01.mp4", "chunk_02.mp4"]
        )
        self.assertEqual(saved["status"], "IN_PROGRESS")
        self.assertEqual(saved["progress_percent"], 40.0)

        # 3. Verifica que é recuperável
        check2 = AutoRenderCrashRecoveryGuard.check_resumable_render(self.project_id)
        self.assertTrue(check2["has_resumable_checkpoint"])
        self.assertEqual(check2["resume_from_scene_index"], 3)
        self.assertEqual(check2["saved_chunks_count"], 2)

        # 4. Limpa checkpoint
        cleared = AutoRenderCrashRecoveryGuard.clear_checkpoint(self.project_id)
        self.assertTrue(cleared)
        check3 = AutoRenderCrashRecoveryGuard.check_resumable_render(self.project_id)
        self.assertFalse(check3["has_resumable_checkpoint"])


if __name__ == "__main__":
    unittest.main()
