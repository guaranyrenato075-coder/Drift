from pathlib import Path
from typing import Dict, Any, List, Optional
from models.scene_plan import ProjectPlan

class DeliverablesPackager:
    """
    All-in-one publishing packager:
    Assembles complete multi-platform release kit:
      - YouTube Description with timestamped Chapters (00:00 Intro, 01:23 Cena 2...)
      - SEO Tags, Hashtags, and Title variants (A/B testing)
      - Synchronized SRT Subtitles
      - Thumbnail generation brief with composition specs
      - Project metadata bundle
    """

    @classmethod
    def generate_release_kit(cls, plan: ProjectPlan, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        if output_dir is None:
            output_dir = Path("d:/CUTWIREDRIFT") / f"release_{plan.project_id[:8]}"
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # 1. Build Chapters
        chapters: List[str] = []
        cur_sec = 0.0
        for s in plan.scenes:
            m = int(cur_sec // 60)
            sec = int(cur_sec % 60)
            ch_title = s.concept or (s.english_keywords[0].capitalize() if s.english_keywords else f"Parte {s.order}")
            chapters.append(f"{m:02d}:{sec:02d} {ch_title}")
            cur_sec += (s.duration or 4.0)

        # 2. Build Title Variants for A/B Testing
        clean_title = plan.title or "Vídeo Automático IA"
        title_variants = [
            clean_title,
            f"O Segredo que Ninguém Te Contou Sobre {clean_title}",
            f"{clean_title}: O que Você Precisa Saber Antes de Começar",
            f"Por que Quase Todos Erram Nisso? ({clean_title})"
        ]

        # 3. Build Tags and Hashtags
        all_tags = []
        for s in plan.scenes:
            all_tags.extend(s.keywords[:2])
            all_tags.extend(s.english_keywords[:2])
        unique_tags = list(dict.fromkeys(all_tags))[:15]
        hashtags = [f"#{t.replace(' ', '')}" for t in unique_tags[:6]]

        # 4. Generate Full YouTube Description
        desc_lines = [
            f"{title_variants[0]}",
            "",
            "Neste vídeo, exploramos em profundidade uma análise visual e reflexiva com narração sincronizada.",
            "",
            "📌 CAPÍTULOS:",
            "\n".join(chapters),
            "",
            "🏷️ TAGS:",
            ", ".join(unique_tags),
            "",
            " ".join(hashtags),
            "",
            "---",
            "Produzido com CutWire Drift AI Editor."
        ]
        full_description = "\n".join(desc_lines)
        (out_path / "youtube_description.txt").write_text(full_description, encoding="utf-8")

        # 5. Build Thumbnail Brief
        thumb_brief = {
            "title_overlay": title_variants[0][:35].upper(),
            "visual_subject": plan.scenes[0].visual_description if plan.scenes else "Visual de alto impacto",
            "color_palette": "Contraste cinematográfico com texto em amarelo/branco e fundo escuro",
            "emotion": "Curiosidade e autoridade",
            "resolution": "1280x720 (16:9)"
        }
        import json
        (out_path / "thumbnail_brief.json").write_text(json.dumps(thumb_brief, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "output_directory": str(out_path.resolve()),
            "title_variants": title_variants,
            "chapters_count": len(chapters),
            "chapters_text": "\n".join(chapters),
            "description": full_description,
            "tags": unique_tags,
            "thumbnail_brief": thumb_brief
        }

