import unittest
from models.scene_plan import MediaCandidate, ProjectPlan, ProjectConfig, Scene
from media.copyright_analyzer import (
    CopyrightAnalyzer,
    CopyrightStatus,
    CopyrightAnalysisResult,
    CopyrightProjectAudit,
)

class TestCopyrightAnalyzer(unittest.TestCase):

    def test_safe_commercial_pexels(self):
        cand = MediaCandidate(
            candidate_id="px_123",
            platform="pexels",
            download_url="https://images.pexels.com/123.mp4",
            title="Pôr do Sol no Mar",
            creator="Jane Doe",
            license="Pexels License"
        )
        res = CopyrightAnalyzer.analyze_candidate(cand)
        self.assertEqual(res.status, CopyrightStatus.VERIFIED_SAFE_COMMERCIAL)
        self.assertTrue(res.is_commercial_allowed)
        self.assertTrue(res.is_derivative_allowed)
        self.assertTrue(res.is_content_id_safe)
        self.assertFalse(res.attribution_required)
        self.assertLessEqual(res.risk_score, 10)
        self.assertEqual(cand.copyright_risk, "safe")
        self.assertTrue(cand.commercial_use)

    def test_safe_public_domain_cc0(self):
        cand = MediaCandidate(
            candidate_id="pd_456",
            platform="archive_org",
            download_url="https://archive.org/film.mp4",
            title="Vintage Moon Launch",
            license="CC0 1.0 Universal (Public Domain)"
        )
        res = CopyrightAnalyzer.analyze_candidate(cand)
        self.assertEqual(res.status, CopyrightStatus.VERIFIED_SAFE_COMMERCIAL)
        self.assertEqual(res.risk_score, 0)
        self.assertTrue(res.is_commercial_allowed)
        self.assertFalse(res.attribution_required)

    def test_safe_with_attribution_cc_by(self):
        cand = MediaCandidate(
            candidate_id="wiki_789",
            platform="wikimedia",
            download_url="https://upload.wikimedia.org/pic.jpg",
            title="Estátua Histórica",
            creator="Carlos Silva",
            page_url="https://commons.wikimedia.org/wiki/File:statue.jpg",
            license="CC-BY-4.0"
        )
        res = CopyrightAnalyzer.analyze_candidate(cand)
        self.assertEqual(res.status, CopyrightStatus.SAFE_WITH_ATTRIBUTION)
        self.assertTrue(res.is_commercial_allowed)
        self.assertTrue(res.is_derivative_allowed)
        self.assertTrue(res.attribution_required)
        self.assertIn("Carlos Silva", res.required_attribution_credit)
        self.assertIn("CC-BY", res.required_attribution_credit)
        self.assertEqual(cand.copyright_risk, "safe")

    def test_restricted_non_commercial_cc_nc(self):
        cand = MediaCandidate(
            candidate_id="flickr_nc",
            platform="flickr",
            download_url="https://flickr.com/art.jpg",
            title="Arte Digital Restrita",
            license="CC-BY-NC-4.0"
        )
        res = CopyrightAnalyzer.analyze_candidate(cand)
        self.assertEqual(res.status, CopyrightStatus.RESTRICTED_NON_COMMERCIAL)
        self.assertFalse(res.is_commercial_allowed)
        self.assertFalse(res.is_content_id_safe)
        self.assertGreaterEqual(res.risk_score, 80)
        self.assertEqual(cand.copyright_risk, "restricted")
        self.assertFalse(cand.commercial_use)

    def test_restricted_no_derivatives_cc_nd(self):
        cand = MediaCandidate(
            candidate_id="cc_nd_1",
            platform="vimeo",
            download_url="https://vimeo.com/video.mp4",
            title="Curta Metragem Fechado",
            license="CC-BY-ND-3.0"
        )
        res = CopyrightAnalyzer.analyze_candidate(cand)
        self.assertEqual(res.status, CopyrightStatus.RESTRICTED_NO_DERIVATIVES)
        self.assertFalse(res.is_derivative_allowed)
        self.assertFalse(res.is_content_id_safe)
        self.assertGreaterEqual(res.risk_score, 80)

    def test_restricted_editorial_only(self):
        cand = MediaCandidate(
            candidate_id="news_1",
            platform="shutterstock",
            download_url="https://shutterstock.com/press.jpg",
            title="Celebridade no Tapete Vermelho (Editorial Use)",
            license="Editorial Use Only"
        )
        res = CopyrightAnalyzer.analyze_candidate(cand)
        self.assertEqual(res.status, CopyrightStatus.RESTRICTED_EDITORIAL)
        self.assertFalse(res.is_commercial_allowed)

    def test_filter_candidates(self):
        c1 = MediaCandidate(candidate_id="1", platform="pexels", license="Pexels")
        c2 = MediaCandidate(candidate_id="2", platform="custom", license="CC-BY-NC")
        c3 = MediaCandidate(candidate_id="3", platform="custom", license="CC-BY-ND")
        c4 = MediaCandidate(candidate_id="4", platform="wikimedia", license="CC-BY-4.0")

        filtered_commercial = CopyrightAnalyzer.filter_candidates([c1, c2, c3, c4], allow_attribution=True, strict_commercial=True)
        # c1 e c4 são comerciais (c2 é NC e c3 é ND)
        self.assertEqual(len(filtered_commercial), 2)
        self.assertEqual([c.candidate_id for c in filtered_commercial], ["1", "4"])

        filtered_no_attrib = CopyrightAnalyzer.filter_candidates([c1, c2, c3, c4], allow_attribution=False, strict_commercial=True)
        # apenas c1 (c4 exige atribuição)
        self.assertEqual(len(filtered_no_attrib), 1)
        self.assertEqual(filtered_no_attrib[0].candidate_id, "1")

    def test_audit_timeline_copyright(self):
        plan = ProjectPlan(
            project_id="audit_proj_1",
            title="Vídeo Sobre O Universo",
            config=ProjectConfig(),
            scenes=[
                Scene(
                    order=1,
                    narration_text="O cosmos é infinito.",
                    selected_media=MediaCandidate(
                        candidate_id="m1",
                        platform="nasa",
                        title="Galáxia de Andrômeda",
                        creator="NASA/JPL",
                        license="Public Domain"
                    )
                ),
                Scene(
                    order=2,
                    narration_text="Grandes cientistas desvendaram seus segredos.",
                    selected_media=MediaCandidate(
                        candidate_id="m2",
                        platform="wikimedia",
                        title="Foto de Galileu",
                        creator="Museu Histórico",
                        license="CC-BY-4.0",
                        page_url="https://commons.wikimedia.org/galileu"
                    )
                ),
                Scene(
                    order=3,
                    narration_text="Cena de demonstração com mídia proibida.",
                    selected_media=MediaCandidate(
                        candidate_id="m3",
                        platform="unknown",
                        title="Vídeo com Copyright Rígido",
                        license="All Rights Reserved"
                    )
                )
            ]
        )

        audit = CopyrightAnalyzer.audit_timeline_copyright(plan)
        self.assertEqual(audit.project_id, "audit_proj_1")
        self.assertEqual(audit.total_scenes_analyzed, 3)
        self.assertEqual(audit.fully_cleared_scenes, 1)
        self.assertEqual(audit.scenes_requiring_attribution, 1)
        self.assertEqual(audit.restricted_scenes_count, 1)
        self.assertFalse(audit.is_safe_for_monetization)
        self.assertGreater(len(audit.actionable_warnings), 0)
        self.assertIn("CRÉDITOS E ATRIBUIÇÕES DE MÍDIA", audit.youtube_description_credits)
        self.assertIn("Foto de Galileu", audit.youtube_description_credits)

if __name__ == "__main__":
    unittest.main()
