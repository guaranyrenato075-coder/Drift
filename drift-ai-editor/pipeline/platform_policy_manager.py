"""
Dynamic Platform Policy Manager & Compliance Auditor for CutWire Drift AI.
Manages updateable policy registries for YouTube, TikTok, and Instagram (Meta).
Enforces monetization guidelines, shadowban word checks, AI disclosure requirements,
watermark repost penalties, and safe-zone boundaries.
Policies can be updated on the fly via local JSON edits, API updates, or remote feeds.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import json
import os
import time

@dataclass
class PolicyFinding:
    platform: str
    rule_category: str
    severity: str  # "violation" (red), "warning" (yellow), "info" (blue)
    affected_scene_order: Optional[int]
    message: str
    remediation_suggestion: str

@dataclass
class PolicyComplianceReport:
    platform: str
    policy_version: str
    is_compliant: bool
    monetization_safe: bool
    risk_score: int  # 0 (perfect) to 100 (high risk of strike/shadowban)
    findings: List[PolicyFinding] = field(default_factory=list)
    actionable_checklist: List[str] = field(default_factory=list)

class PlatformPolicyManager:
    """
    Updateable regulatory compliance engine for YouTube, TikTok, and Instagram.
    """

    DEFAULT_POLICY_PATH = Path(__file__).resolve().parent.parent / "storage" / "platform_policies.json"

    def __init__(self, policy_path: Optional[Path] = None):
        self.policy_path = policy_path or self.DEFAULT_POLICY_PATH
        self.policies: Dict[str, Any] = {}
        self.load_policies()

    def load_policies(self):
        """Loads policy definition JSON from disk."""
        if self.policy_path.exists():
            try:
                self.policies = json.loads(self.policy_path.read_text(encoding="utf-8"))
                return
            except Exception:
                pass
        self._set_default_policies()

    def save_policies(self):
        """Persists current policy dictionary to disk."""
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)
        self.policies["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.policy_path.write_text(json.dumps(self.policies, indent=2, ensure_ascii=False), encoding="utf-8")

    def update_policy_rule(self, platform: str, path_keys: List[str], value: Any) -> bool:
        """
        Updates a specific policy rule (e.g., ['youtube', 'monetization', 'profanity_first_seconds_limit'] -> 8.0)
        and persists immediately.
        """
        if "platforms" not in self.policies or platform not in self.policies["platforms"]:
            return False

        target = self.policies["platforms"][platform]
        for key in path_keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]

        target[path_keys[-1]] = value
        self.save_policies()
        return True

    def import_policy_update(self, new_policy_data: Dict[str, Any]) -> str:
        """
        Merges or overwrites policy database with an updated version from remote server or JSON payload.
        """
        if "platforms" in new_policy_data:
            self.policies["platforms"].update(new_policy_data["platforms"])
            if "version" in new_policy_data:
                self.policies["version"] = new_policy_data["version"]
            self.save_policies()
            return self.policies.get("version", "custom")
        return "invalid_data"

    def get_platform_policy(self, platform: str) -> Dict[str, Any]:
        return self.policies.get("platforms", {}).get(platform.lower(), {})

    def audit_project(self, plan: Any, platform: str = "youtube") -> PolicyComplianceReport:
        """
        Audits a ProjectPlan against the requested platform's current policy registry.
        """
        plat = platform.lower()
        policy = self.get_platform_policy(plat)
        findings: List[PolicyFinding] = []
        checklist: List[str] = []

        if not policy:
            return PolicyComplianceReport(plat, "unknown", True, True, 0, [], ["Platform policy not found."])

        # -------------------------------------------------------------
        # 1. YOUTUBE AUDIT
        # -------------------------------------------------------------
        if plat == "youtube":
            monet = policy.get("monetization", {})
            first_sec_limit = monet.get("profanity_first_seconds_limit", 7.0)
            restricted = monet.get("restricted_topics", [])

            # Check title length
            meta = policy.get("metadata", {})
            max_title = meta.get("max_title_chars", 100)
            if plan.title and len(plan.title) > max_title:
                findings.append(
                    PolicyFinding(
                        platform="youtube",
                        rule_category="metadata",
                        severity="warning",
                        affected_scene_order=None,
                        message=f"Title exceeds {max_title} characters ({len(plan.title)} chars).",
                        remediation_suggestion="Shorten title under 65 chars for optimal YouTube mobile display."
                    )
                )

            # Check scene narration
            current_time = 0.0
            for s in getattr(plan, "scenes", []):
                t_lower = s.narration_text.lower()
                dur = getattr(s, "duration", 4.0)

                # Check profanity in opening seconds
                if current_time < first_sec_limit:
                    common_profanity = ["porra", "caralho", "merda", "fuck", "shit", "bitch"]
                    for p_word in common_profanity:
                        if p_word in t_lower:
                            findings.append(
                                PolicyFinding(
                                    platform="youtube",
                                    rule_category="monetization_advertiser_guidelines",
                                    severity="violation",
                                    affected_scene_order=s.order,
                                    message=f"Profanity '{p_word}' detected in first {first_sec_limit}s of video.",
                                    remediation_suggestion="Remove or beep profanity in the opening 7s to retain full green monetization."
                                )
                            )

                # Check restricted monetization topics
                for topic in restricted:
                    if topic.lower() in t_lower:
                        findings.append(
                            PolicyFinding(
                                platform="youtube",
                                rule_category="monetization_restricted_topics",
                                severity="violation",
                                affected_scene_order=s.order,
                                message=f"Restricted advertiser topic detected: '{topic}'.",
                                remediation_suggestion=f"Rephrase content regarding '{topic}' to avoid yellow dollar icon."
                            )
                        )

                current_time += dur

            # AI Disclosure checklist item
            if policy.get("ai_disclosure", {}).get("required"):
                checklist.append("YouTube Studio: Marque a opção 'Conteúdo Alterado ou Sintético' (AI Disclosure).")

        # -------------------------------------------------------------
        # 2. TIKTOK AUDIT
        # -------------------------------------------------------------
        elif plat == "tiktok":
            comm = policy.get("community_guidelines", {})
            shadow_words = comm.get("shadowban_risk_words", [])

            for s in getattr(plan, "scenes", []):
                t_lower = s.narration_text.lower()
                for word in shadow_words:
                    if word.lower() in t_lower:
                        findings.append(
                            PolicyFinding(
                                platform="tiktok",
                                rule_category="shadowban_prevention",
                                severity="violation",
                                affected_scene_order=s.order,
                                message=f"High-risk shadowban term detected in narration: '{word}'.",
                                remediation_suggestion=f"Replace '{word}' with softer alternative to avoid TikTok suppression."
                            )
                        )

            # Safe zone reminder
            checklist.append("Verifique se as legendas respeitam a margem inferior de 280px (área de descrição do TikTok).")
            checklist.append("Ative o selo 'Gerado por IA' ao postar no aplicativo.")

        # -------------------------------------------------------------
        # 3. INSTAGRAM REELS AUDIT
        # -------------------------------------------------------------
        elif plat in ("instagram", "reels"):
            algo = policy.get("algorithm_guidelines", {})
            watermarks = algo.get("prohibited_watermarks", [])
            bait_words = algo.get("engagement_bait_words", [])

            # Check for forbidden watermarks in media candidate filenames or descriptions
            for s in getattr(plan, "scenes", []):
                med = getattr(s, "selected_media", None)
                if med:
                    title_med = (med.title or "").lower()
                    for wm in watermarks:
                        if wm in title_med:
                            findings.append(
                                PolicyFinding(
                                    platform="instagram",
                                    rule_category="repost_watermark_penalty",
                                    severity="violation",
                                    affected_scene_order=s.order,
                                    message=f"Potential competitor watermark detected in media: '{wm}'.",
                                    remediation_suggestion="Instagram Reels heavily demotes videos with TikTok watermarks. Use clean asset."
                                )
                            )

                t_lower = s.narration_text.lower()
                for bait in bait_words:
                    if bait.lower() in t_lower:
                        findings.append(
                            PolicyFinding(
                                platform="instagram",
                                rule_category="engagement_bait",
                                severity="warning",
                                affected_scene_order=s.order,
                                message=f"Engagement bait phrase detected: '{bait}'.",
                                remediation_suggestion="Avoid explicit algorithmic engagement bait to maintain organic reach."
                            )
                        )

            checklist.append("Certifique-se de que os primeiros 125 caracteres da legenda transmitam o gancho principal.")
            checklist.append("Marque o rótulo 'Criado com IA' nas configurações avançadas do Instagram.")

        # Compute overall status
        violations = [f for f in findings if f.severity == "violation"]
        is_compliant = len(violations) == 0
        risk_score = min(100, len(violations) * 35 + len(findings) * 10)

        return PolicyComplianceReport(
            platform=plat,
            policy_version=self.policies.get("version", "2026.10.1"),
            is_compliant=is_compliant,
            monetization_safe=is_compliant,
            risk_score=risk_score,
            findings=findings,
            actionable_checklist=checklist
        )

    def _set_default_policies(self):
        self.policies = {
            "version": "2026.10.1",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "platforms": {
                "youtube": {
                    "monetization": {"profanity_first_seconds_limit": 7.0, "restricted_topics": ["terrorismo", "drogas ilícitas"]},
                    "ai_disclosure": {"required": True},
                    "metadata": {"max_title_chars": 100}
                },
                "tiktok": {
                    "community_guidelines": {"shadowban_risk_words": ["compre seguidores", "ganhe dinheiro rapido"]},
                    "ai_disclosure": {"required": True}
                },
                "instagram": {
                    "algorithm_guidelines": {
                        "prohibited_watermarks": ["tiktok", "bytedance"],
                        "engagement_bait_words": ["comente 'eu quero'", "siga para não ter azar"]
                    },
                    "ai_disclosure": {"required": True}
                }
            }
        }
        self.save_policies()
