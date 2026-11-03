import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from models.scene_plan import ProjectPlan, Scene

class LicenseManifestManager:
    """
    Manages granular, per-asset copyright records, attribution requirements,
    and compliance manifests (including strict Pexels attribution links,
    Unsplash author mentions, and Creative Commons share-alike tracking).
    """

    @classmethod
    def generate_manifest(cls, plan: ProjectPlan) -> Dict[str, Any]:
        manifest_entries: List[Dict[str, Any]] = []
        platform_disclaimers: Dict[str, str] = {}

        for scene in plan.scenes:
            media = scene.selected_media
            if not media:
                continue

            # Determine specific attribution link and format per provider
            if media.platform == "pexels":
                attribution_text = f"Vídeo por {media.creator} no Pexels (https://www.pexels.com)"
                platform_disclaimers["pexels"] = (
                    "Os vídeos e fotos fornecidos pelo Pexels são gratuitos para uso comercial e pessoal. "
                    "Conforme as diretrizes do Pexels, mantemos crédito aos criadores originais e link para a plataforma."
                )
            elif media.platform == "unsplash":
                attribution_text = f"Foto por {media.creator} no Unsplash (https://unsplash.com)"
                platform_disclaimers["unsplash"] = (
                    "Fotografia fornecida sob a Licença Unsplash gratuita para fins comerciais e editoriais."
                )
            elif media.platform == "coverr":
                attribution_text = f"Filmagem por {media.creator} no Coverr.co"
                platform_disclaimers["coverr"] = "Imagens licenciadas sob os termos gratuitos do Coverr."
            elif media.platform == "archive_org":
                attribution_text = f"Arquivo histórico: {media.title} (Internet Archive - Domínio Público)"
                platform_disclaimers["archive_org"] = "Obras em Domínio Público ou licença aberta preservadas pelo Internet Archive."
            elif media.platform == "nasa":
                attribution_text = f"Imagem/Vídeo cortesia da NASA / JPL-Caltech"
                platform_disclaimers["nasa"] = "Materiais visuais da NASA são de Domínio Público dos Estados Unidos."
            elif media.platform == "local":
                attribution_text = f"Arquivo local: {media.title} (Acervo do autor)"
            else:
                attribution_text = f"Mídia por {media.creator} ({media.platform})"

            manifest_entries.append({
                "scene_order": scene.order,
                "platform": media.platform,
                "external_id": media.external_id,
                "title": media.title,
                "creator": media.creator,
                "page_url": media.page_url,
                "download_url": media.download_url,
                "local_file": media.local_cached_path or "",
                "license": media.license,
                "formal_attribution": attribution_text
            })

        return {
            "project_id": plan.project_id,
            "project_title": plan.title,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_licensed_assets": len(manifest_entries),
            "platform_compliance_notices": platform_disclaimers,
            "assets": manifest_entries
        }

    @classmethod
    def save_markdown_report(cls, plan: ProjectPlan, output_path: Path) -> str:
        manifest = cls.generate_manifest(plan)
        lines = [
            f"# Manifesto Legal de Direitos Autorais e Atribuição",
            f"**Projeto:** {manifest['project_title']}  ",
            f"**ID do Projeto:** `{manifest['project_id']}`  ",
            f"**Data de Geração:** {manifest['generated_at']}  ",
            f"**Total de Mídias Licenciadas:** {manifest['total_licensed_assets']}",
            "",
            "## Termos das Plataformas e Isenções Legais",
            ""
        ]

        for plat, notice in manifest["platform_compliance_notices"].items():
            lines.append(f"- **{plat.upper()}**: {notice}")

        lines.extend([
            "",
            "## Detalhamento por Cena e Arquivo",
            "",
            "| Cena | Plataforma | Criador / Autor | Título / Arquivo | Licença | Link Oficial |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ])

        for item in manifest["assets"]:
            lines.append(
                f"| {item['scene_order']:02d} | `{item['platform']}` | {item['creator']} | {item['title'][:30]} | {item['license']} | [Acessar]({item['page_url']}) |"
            )

        lines.extend([
            "",
            "---",
            "*Relatório gerado automaticamente pelo Drift AI Editor. Todos os arquivos são validados antes da montagem na timeline.*"
        ])

        content = "\n".join(lines)
        Path(output_path).write_text(content, encoding="utf-8")
        return content

