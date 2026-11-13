import unittest
from director.micro_hook_retention_cadence_engine import MicroHookRetentionCadenceEngine


class TestMicroHookRetentionCadenceEngine(unittest.TestCase):
    def test_plan_micro_hook_injections(self):
        plan = MicroHookRetentionCadenceEngine.plan_micro_hook_injections(video_duration_sec=60.0, cadence_interval_sec=8.0)
        self.assertEqual(plan["status"], "success")
        self.assertGreater(plan["total_micro_hooks_planned"], 3)
        self.assertGreater(plan["projected_retention_lift_pct"], 20.0)
        self.assertTrue(plan["audience_dropoff_mitigated"])

    def test_audit_scene_cadence(self):
        scenes = [
            {"id": "scene_short", "duration": 4.0},
            {"id": "scene_long", "duration": 14.0}
        ]
        audit = MicroHookRetentionCadenceEngine.audit_scene_cadence(scenes)
        self.assertEqual(audit["status"], "success")
        self.assertEqual(audit["dead_zones_found"], 1)
        self.assertEqual(audit["dead_zones"][0]["scene_id"], "scene_long")


if __name__ == "__main__":
    unittest.main()
