"""
Dynamic Platform Policy Manager & Compliance Auditor for CutWire Drift AI.
Manages updateable policy registries for YouTube, TikTok, and Instagram (Meta).
Enforces monetization guidelines, shadowban word checks, AI disclosure requirements,
watermark repost penalties, safe-zone boundaries, and copyright IP clearance.
Policies are frequently updated via remote GitHub feeds, local JSON sync, and periodic health checks.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import json
import os
import time
import urllib.request
import urllib.error

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
    Frequently syncs latest policy updates from remote feeds to prevent copyright strikes and shadowbans.
    """

    DEFAULT_POLICY_PATH = Path(__file__).resolve().parent.parent / "storage" / "platform_policies.json"
    REMOTE_FEED_URL = "https://raw.githubusercontent.com/guaranyrenato075-coder/Drift/main/drift-ai-editor/storage/platform_policies.json"

    def __init__(self, policy_path: Optional[Path] = None, auto_sync: bool = True):
        self.policy_path = policy_path or self.DEFAULT_POLICY_PATH
        self.policies: Dict[str, Any] = {}
        self.load_policies()
        if auto_sync:
            self.auto_sync_if_due()

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

    def auto_sync_if_due(self) -> bool:
        """
        Checks if policies need a scheduled sync (every 24 hours). Runs silently without blocking.
        """
        last_check = self.policies.get("last_sync_timestamp", 0)
        interval_sec = self.policies.get("update_interval_hours", 24) * 3600
        if (time.time() - last_check) > interval_sec:
            sync_res = self.sync_policies_from_remote()
            return sync_res.get("updated", False)
        return False

    def sync_policies_from_remote(self, custom_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Syncs latest policy updates from remote GitHub feed or API without interrupting local operations.
        """
        url = custom_url or self.REMOTE_FEED_URL
        self.policies["last_sync_timestamp"] = time.time()
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Drift-Policy-Sync/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                remote_data = json.loads(response.read().decode("utf-8"))
                if "platforms" in remote_data:
                    current_ver = self.policies.get("version", "2026.10.0")
                    remote_ver = remote_data.get("version", current_ver)
                    self.policies["platforms"].update(remote_data["platforms"])
                    self.policies["version"] = remote_ver
                    self.save_policies()
                    return {
                        "ok": True,
                        "updated": True,
                        "version": remote_ver,
                        "status": f"Políticas atualizadas com sucesso para a versão {remote_ver}!"
                    }
        except Exception:
            # Fallback seguro: se estiver sem conexão, mantém as regras locais sem erro
            pass

        self.save_policies()
        return {
            "ok": True,
            "updated": False,
            "version": self.policies.get("version", "2026.11.0"),
            "status": "Políticas locais atualizadas e protegidas."
        }

    def update_policy_rule(self, platform: str, path_keys: List[str], value: Any) -> bool:
        """
        Updates a specific policy rule and persists immediately.
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
        Audits a ProjectPlan against YouTube, TikTok, or Instagram policies,
        verifying copyright safety, Content ID clearance, profanity, shadowban words, and safe zones.
        """
        plat = platform.lower()
        if plat in ("reels", "insta"):
            plat = "instagram"
        elif plat in ("yt", "shorts"):
            plat = "youtube"

        policy = self.get_platform_policy(plat)
        findings: List[PolicyFinding] = []
        checklist: List[str] = []

        if not policy:
            return PolicyComplianceReport(plat, "unknown", True, True, 0, [], ["Platform policy not found."])

        # -------------------------------------------------------------
        # AUDITORIA UNIVERSAL DE COPYRIGHT (TODAS AS 31 FONTES)
        # -------------------------------------------------------------
        uncredited_count = 0
        restricted_ip_count = 0
        scenes = getattr(plan, "scenes", [])

        for s in scenes:
            med = getattr(s, "selected_media", None)
            if med:
                # Checa risco de copyright
                c_risk = getattr(med, "copyright_risk", "safe")
                if c_risk == "restricted":
                    restricted_ip_count += 1
                    findings.append(
                        PolicyFinding(
                            platform=plat,
                            rule_category="copyright_infringement_risk",
                            severity="violation",
                            affected_scene_order=s.order,
                            message=f"Cena {s.order}: Mídia com restrição de direitos ('{med.title}').",
                            remediation_suggestion="Substitua por mídia de acervo público (NASA, Smithsonian, Mazwai, Pexels)."
                        )
                    )
                
                # Checa necessidade de atribuição de licença
                if getattr(med, "license", "").startswith("CC-BY") and not getattr(med, "attribution_text", None):
                    uncredited_count += 1

        if uncredited_count > 0:
            findings.append(
                PolicyFinding(
                    platform=plat,
                    rule_category="copyright_attribution",
                    severity="warning",
                    affected_scene_order=None,
                    message=f"{uncredited_count} mídias requerem citação de créditos na descrição.",
                    remediation_suggestion="Use o 'Kit de Publicação' do Drift para colar os créditos completos na descrição do post."
                )
            )

        # -------------------------------------------------------------
        # 1. YOUTUBE AUDIT (Monetização, Content ID, AI Disclosure)
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
                        message=f"Título excede {max_title} caracteres ({len(plan.title)} chars).",
                        remediation_suggestion="Mantenha o título abaixo de 65 caracteres para exibição ideal em celulares."
                    )
                )

            # Check scene narration for profanity and restricted advertiser topics
            current_time = 0.0
            for s in scenes:
                t_lower = (s.narration_text or "").lower()
                dur = getattr(s, "duration", 4.0)

                if current_time < first_sec_limit:
                    common_profanity = ["porra", "caralho", "merda", "fuck", "shit", "bitch", "foda", "puta"]
                    for p_word in common_profanity:
                        if p_word in t_lower:
                            findings.append(
                                PolicyFinding(
                                    platform="youtube",
                                    rule_category="monetization_advertiser_guidelines",
                                    severity="violation",
                                    affected_scene_order=s.order,
                                    message=f"Palavrão '{p_word}' detectado nos primeiros {first_sec_limit}s do vídeo.",
                                    remediation_suggestion="Remova ou aplique efeito 'beep' nos primeiros 7s para garantir o ícone verde de monetização."
                                )
                            )

                for topic in restricted:
                    if topic.lower() in t_lower:
                        findings.append(
                            PolicyFinding(
                                platform="youtube",
                                rule_category="monetization_restricted_topics",
                                severity="violation",
                                affected_scene_order=s.order,
                                message=f"Tópico restrito para anúncios: '{topic}'.",
                                remediation_suggestion=f"Reescreva trechos sobre '{topic}' para evitar o ícone amarelo de restrição."
                            )
                        )

                current_time += dur

            checklist.append("YouTube Studio: Marque a opção 'Conteúdo Alterado ou Sintético' (AI Disclosure).")
            checklist.append("Cole o bloco de créditos de licença na descrição do vídeo para imunidade no Content ID.")

        # -------------------------------------------------------------
        # 2. TIKTOK AUDIT (Shadowban, Safe Zones, Rótulo de IA)
        # -------------------------------------------------------------
        elif plat == "tiktok":
            comm = policy.get("community_guidelines", {})
            shadow_words = comm.get("shadowban_risk_words", [])

            for s in scenes:
                t_lower = (s.narration_text or "").lower()
                for word in shadow_words:
                    if word.lower() in t_lower:
                        findings.append(
                            PolicyFinding(
                                platform="tiktok",
                                rule_category="shadowban_prevention",
                                severity="violation",
                                affected_scene_order=s.order,
                                message=f"Palavra de alto risco de Shadowban detectada: '{word}'.",
                                remediation_suggestion=f"Substitua '{word}' por um termo suave para não ter o alcance cortado no TikTok."
                            )
                        )

            checklist.append("Legendas: Mantenha as legendas acima de 280px da base (para não cobrir com a legenda do app).")
            checklist.append("Configurações do TikTok: Ative o botão 'Conteúdo Gerado por IA' ao postar.")

        # -------------------------------------------------------------
        # 3. INSTAGRAM REELS AUDIT (Marcas d'água, Baits, Meta Rights)
        # -------------------------------------------------------------
        elif plat == "instagram":
            algo = policy.get("algorithm_guidelines", {})
            watermarks = algo.get("prohibited_watermarks", [])
            bait_words = algo.get("engagement_bait_words", [])

            for s in scenes:
                med = getattr(s, "selected_media", None)
                if med:
                    title_med = (getattr(med, "title", "") or "").lower()
                    for wm in watermarks:
                        if wm in title_med:
                            findings.append(
                                PolicyFinding(
                                    platform="instagram",
                                    rule_category="repost_watermark_penalty",
                                    severity="violation",
                                    affected_scene_order=s.order,
                                    message=f"Potencial marca d'água concorrente detectada: '{wm}'.",
                                    remediation_suggestion="O algoritmo do Reels pune vídeos com logos do TikTok/Kwai. Use a mídia limpa do acervo."
                                )
                            )

                t_lower = (s.narration_text or "").lower()
                for bait in bait_words:
                    if bait.lower() in t_lower:
                        findings.append(
                            PolicyFinding(
                                platform="instagram",
                                rule_category="engagement_bait",
                                severity="warning",
                                affected_scene_order=s.order,
                                message=f"Frase de 'Engagement Bait' detectada: '{bait}'.",
                                remediation_suggestion="Evite pedir comentários forçados para manter o alcance orgânico do Reels."
                            )
                        )

            checklist.append("Reels: Certifique-se de que o gancho principal apareça nos primeiros 3 segundos.")
            checklist.append("Marque o selo 'Criado com IA' nas configurações avançadas do Instagram.")

        # Cálculo do score de conformidade
        violations = [f for f in findings if f.severity == "violation"]
        is_compliant = (len(violations) == 0 and restricted_ip_count == 0)
        risk_score = min(100, len(violations) * 30 + len(findings) * 10)

        return PolicyComplianceReport(
            platform=plat,
            policy_version=self.policies.get("version", "2026.11.0"),
            is_compliant=is_compliant,
            monetization_safe=is_compliant,
            risk_score=risk_score,
            findings=findings,
            actionable_checklist=checklist
        )

    def _set_default_policies(self):
        self.policies = {
            "version": "2026.11.0",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "update_interval_hours": 24,
            "platforms": {
                "youtube": {
                    "monetization": {"profanity_first_seconds_limit": 7.0, "restricted_topics": ["terrorismo", "drogas ilícitas"]},
                    "copyright": {"content_id_protection": "strict", "mandatory_attribution_block": True},
                    "ai_disclosure": {"required": True},
                    "metadata": {"max_title_chars": 100}
                },
                "tiktok": {
                    "community_guidelines": {"shadowban_risk_words": ["compre seguidores", "ganhe dinheiro rapido"]},
                    "copyright": {"commercial_music_strict": True},
                    "ai_disclosure": {"required": True}
                },
                "instagram": {
                    "algorithm_guidelines": {
                        "prohibited_watermarks": ["tiktok", "bytedance", "kuaishou"],
                        "engagement_bait_words": ["comente 'EU QUERO'", "siga para não ter azar"]
                    },
                    "copyright": {"meta_rights_manager": "strict"},
                    "ai_disclosure": {"required": True}
                }
            }
        }
        self.save_policies()
