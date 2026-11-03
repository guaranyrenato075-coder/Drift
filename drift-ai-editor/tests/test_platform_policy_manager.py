"""
Unit and integration tests for Platform Policy Manager in CutWire Drift AI.
Verifies updateable policy registries for YouTube, TikTok, and Instagram,
dynamic rule modifications, and automated compliance auditing.
"""
import unittest
import tempfile
import json
from pathlib import Path
from models.scene_plan import ProjectPlan, Scene, MediaCandidate
from pipeline.platform_policy_manager import PlatformPolicyManager, PolicyComplianceReport

class TestPlatformPolicyManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.policy_file = Path(self.temp_dir.name) / "test_policies.json"
        self.mgr = PlatformPolicyManager(policy_path=self.policy_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_policies_initialized(self):
        self.assertIn("youtube", self.mgr.policies.get("platforms", {}))
        self.assertIn("tiktok", self.mgr.policies.get("platforms", {}))
        self.assertIn("instagram", self.mgr.policies.get("platforms", {}))

    def test_update_policy_rule(self):
        # Update YouTube first seconds limit from 7.0 to 10.0
        success = self.mgr.update_policy_rule("youtube", ["monetization", "profanity_first_seconds_limit"], 10.0)
        self.assertTrue(success)
        reloaded = PlatformPolicyManager(policy_path=self.policy_file)
        yt_policy = reloaded.get_platform_policy("youtube")
        self.assertEqual(yt_policy["monetization"]["profanity_first_seconds_limit"], 10.0)

    def test_import_policy_update(self):
        new_payload = {
            "version": "2026.11.0",
            "platforms": {
                "youtube": {
                    "monetization": {
                        "profanity_first_seconds_limit": 5.0,
                        "restricted_topics": ["novo_topico_proibido"]
                    }
                }
            }
        }
        ver = self.mgr.import_policy_update(new_payload)
        self.assertEqual(ver, "2026.11.0")
        self.assertEqual(self.mgr.get_platform_policy("youtube")["monetization"]["profanity_first_seconds_limit"], 5.0)

    def test_youtube_compliance_audit(self):
        plan = ProjectPlan(title="Video com Palavrão no Começo")
        plan.scenes = [
            Scene(order=1, narration_text="Que porra é essa que aconteceu?", duration=3.0),
            Scene(order=2, narration_text="Isso envolve drogas ilícitas no mercado negro.", duration=4.0),
            Scene(order=3, narration_text="Mas tudo terminou com paz e tranquilidade.", duration=5.0)
        ]
        report = self.mgr.audit_project(plan, "youtube")
        self.assertFalse(report.is_compliant)
        self.assertGreater(report.risk_score, 50)
        # Check findings
        categories = [f.rule_category for f in report.findings]
        self.assertIn("monetization_advertiser_guidelines", categories)
        self.assertIn("monetization_restricted_topics", categories)

    def test_tiktok_shadowban_audit(self):
        plan = ProjectPlan(title="Como Ficar Rico")
        plan.scenes = [
            Scene(order=1, narration_text="Descubra como ganhe dinheiro rapido sem sair de casa.", duration=4.0),
            Scene(order=2, narration_text="Trabalho sério e consistência são essenciais.", duration=4.0)
        ]
        report = self.mgr.audit_project(plan, "tiktok")
        self.assertFalse(report.is_compliant)
        self.assertIn("shadowban_prevention", [f.rule_category for f in report.findings])
        self.assertGreater(len(report.actionable_checklist), 0)

    def test_instagram_watermark_and_bait_audit(self):
        plan = ProjectPlan(title="Reels Test")
        scene1 = Scene(order=1, narration_text="Veja este conteúdo incrível.", duration=4.0)
        scene1.selected_media = MediaCandidate(
            platform="pexels", external_id="123", title="Video Clip with TikTok Watermark",
            preview_url="", download_url="", creator="User", page_url="", license="Free"
        )
        scene2 = Scene(order=2, narration_text="comente 'EU QUERO' para receber o link.", duration=3.0)
        plan.scenes = [scene1, scene2]

        report = self.mgr.audit_project(plan, "instagram")
        self.assertFalse(report.is_compliant)
        cats = [f.rule_category for f in report.findings]
        self.assertIn("repost_watermark_penalty", cats)
        self.assertIn("engagement_bait", cats)

if __name__ == "__main__":
    unittest.main()

