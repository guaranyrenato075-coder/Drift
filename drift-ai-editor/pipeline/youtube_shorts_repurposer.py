"""
YouTube Shorts & Vertical Video Repurposer.
Identifica os 3 momentos de maior retenção/clímax de um vídeo longo horizontal (16:9)
e gera planos de corte para Shorts verticais (9:16) com blur stack e ganchos de topo.
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class YouTubeShortsRepurposer:
    """Extrai momentos virais de projetos longos e formata para Shorts 9:16."""

    @classmethod
    def generate_shorts_packages(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Calcula até 3 recortes verticais virais a partir do plano do projeto."""
        scenes = getattr(plan, "scenes", [])
        raw_title = getattr(plan, "title", "Vídeo Principal") or "Vídeo Principal"
        
        shorts_candidates = []
        current_time = 0.0

        for idx, scene in enumerate(scenes):
            duration = float(getattr(scene, "duration", 5.0))
            text = getattr(scene, "narration_text", "") or getattr(scene, "text", "") or ""
            
            # Avalia potencial viral da cena
            viral_score = 70
            hook_words = ["segredo", "nunca", "verdade", "incrível", "chocante", "como", "erro", "milhões", "perigo"]
            found_hooks = [w for w in hook_words if re.search(rf"\b{w}\b", text, re.IGNORECASE)]
            viral_score += len(found_hooks) * 8
            
            if duration >= 4.0:
                # Estima uma fatia de 30 a 50 segundos em torno desse momento
                start_sec = max(0.0, round(current_time - 2.0, 1))
                end_sec = round(start_sec + min(duration + 20.0, 55.0), 1)
                
                hook_headline = f"O SEGREDO: {found_hooks[0].upper()}" if found_hooks else "MOMENTO CHAVE"
                
                shorts_candidates.append({
                    "short_id": f"short_{idx + 1}",
                    "title": f"Parte {len(shorts_candidates) + 1} - {raw_title}",
                    "hook_headline": hook_headline,
                    "target_aspect_ratio": "9:16",
                    "start_time": start_sec,
                    "end_time": end_sec,
                    "duration": round(end_sec - start_sec, 1),
                    "viral_potential_score": min(viral_score, 99),
                    "framing_mode": "smart_blur_stack",
                    "ffmpeg_filter": "split[v1][v2];[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];[v2]scale=1080:-1[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
                })

            current_time += duration

        # Ordena pelos com maior potencial viral e seleciona até 3
        shorts_candidates.sort(key=lambda s: s["viral_potential_score"], reverse=True)
        top_shorts = shorts_candidates[:3]

        return {
            "source_title": raw_title,
            "total_shorts_generated": len(top_shorts),
            "shorts": top_shorts,
            "export_resolution": "1080x1920 (9:16 Vertical)",
            "supported_platforms": ["YouTube Shorts", "TikTok", "Instagram Reels"]
        }
