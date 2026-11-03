from typing import List
from pathlib import Path
import time
from models.scene_plan import ProjectPlan, Provenance

class AttributionManager:
    """
    Tracks provenance and generates attribution & licensing reports for the project.
    """

    @staticmethod
    def generate_report(plan: ProjectPlan) -> str:
        lines: List[str] = [
            f"# Relatório de Procedência e Licenças de Mídia",
            f"**Projeto:** {plan.title}",
            f"**ID do Projeto:** `{plan.project_id}`",
            f"**Data de Geração:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total de Cenas:** {len(plan.scenes)}",
            "",
            "## Clipes Utilizados por Cena",
            ""
        ]

        for scene in plan.scenes:
            lines.append(f"### Cena {scene.order:02d}")
            lines.append(f"- **Narração:** {scene.narration_text}")
            lines.append(f"- **Duração:** {scene.duration:.2f}s")
            
            if scene.provenance:
                p = scene.provenance
                lines.append(f"- **Plataforma:** {p.platform.title()}")
                lines.append(f"- **ID Externo:** `{p.item_id}`")
                lines.append(f"- **Criador / Autor:** {p.creator}")
                lines.append(f"- **Licença:** {p.license}")
                lines.append(f"- **Página de Origem:** [{p.page_url}]({p.page_url})")
                lines.append(f"- **Termos de Busca:** `{p.query}`")
                lines.append(f"- **Arquivo Local:** `{p.local_path}`")
            elif scene.selected_media:
                m = scene.selected_media
                lines.append(f"- **Plataforma:** {m.platform.title()}")
                lines.append(f"- **Criador:** {m.creator}")
                lines.append(f"- **Licença:** {m.license}")
                lines.append(f"- **Página:** [{m.page_url}]({m.page_url})")
            else:
                lines.append(f"- *Nenhum clipe de vídeo associado.*")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def save_report(plan: ProjectPlan, output_path: Path | str):
        content = AttributionManager.generate_report(plan)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

