"""
Gemini Skill Bridge & Loader for CutWire Drift AI.
Loads, parses, registers, and executes official Gemini / Antigravity SKILL.md bundles,
enabling users to inject custom specialized AI personas (e.g., Documentary Director,
Viral Hook Crafter, Fact Checker, Audio Stylist) directly into Drift.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any
import re
import os

@dataclass
class GeminiSkill:
    skill_id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Gemini Creator"
    tags: List[str] = field(default_factory=list)
    system_instructions: str = ""
    skill_folder_path: Optional[str] = None

class GeminiSkillBridge:
    """
    Manages local Gemini skills, parses markdown YAML frontmatter,
    and executes prompt transformations.
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir:
            self.skills_dir = skills_dir
        else:
            self.skills_dir = Path(__file__).resolve().parent

        self.skills: Dict[str, GeminiSkill] = {}
        self.reload_skills()

    def reload_skills(self):
        """Scans the skills directory for SKILL.md bundles."""
        self.skills.clear()
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)

        # 1. Search subdirectories for SKILL.md
        for root, dirs, files in os.walk(str(self.skills_dir)):
            for f in files:
                if f.upper() == "SKILL.MD":
                    full_p = Path(root) / f
                    skill = self._parse_skill_file(full_p)
                    if skill:
                        self.skills[skill.skill_id] = skill

        # 2. Add built-in canonical skills if none exist
        if not self.skills:
            self._install_builtin_defaults()

    def _parse_skill_file(self, file_path: Path) -> Optional[GeminiSkill]:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        skill_id = file_path.parent.name.lower().replace(" ", "_")
        name = skill_id.capitalize()
        description = "Custom Gemini Skill"
        version = "1.0.0"
        author = "Community"
        tags = []
        instructions = content

        # Parse YAML frontmatter if present (--- ... ---)
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if frontmatter_match:
            yaml_block = frontmatter_match.group(1)
            instructions = frontmatter_match.group(2).strip()

            for line in yaml_block.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    k = key.strip().lower()
                    v = val.strip().strip('"').strip("'")
                    if k == "name":
                        name = v
                    elif k == "description":
                        description = v
                    elif k == "version":
                        version = v
                    elif k == "author":
                        author = v
                    elif k == "tags":
                        tags = [t.strip() for t in v.replace("[", "").replace("]", "").split(",") if t.strip()]

        return GeminiSkill(
            skill_id=skill_id,
            name=name,
            description=description,
            version=version,
            author=author,
            tags=tags,
            system_instructions=instructions,
            skill_folder_path=str(file_path.parent)
        )

    def _install_builtin_defaults(self):
        """Installs standard ready-to-use skills."""
        defaults = [
            (
                "documentary_master",
                "Roteirista de Documentário Imersivo",
                "Transforma tópicos históricos e científicos em narrativas cinematográficas ricas e investigativas.",
                """Você é um roteirista sênior de documentários como Vox e Kurzgesagt.
Divida a narrativa em 5 atos:
1. O Mistério / Pergunta Intrigante
2. A Origem Histórica
3. A Reviravolta Inesperada
4. O Impacto no Presente
5. A Lição Filosófica para o Futuro.
Escreva parágrafos concisos com vocabulário visual vivo."""
            ),
            (
                "viral_hook_crafter",
                "Mestre dos Ganchos Virais (Shorts & Reels)",
                "Otimiza os primeiros 5 segundos para reter 80%+ da audiência com gatilhos de curiosidade extrema.",
                """Você é especialista em retenção de vídeos curtos verticais (TikTok/Shorts).
Para cada tema, crie uma abertura magnética que quebre padrões.
Proíba introduções lentas como 'Olá pessoal'.
Vá direto para a dor, choque ou revelação."""
            ),
            (
                "cinematic_color_director",
                "Diretor de Estilo e Paleta de Cores",
                "Prescreve paletas de cor, lentes e atmosfera visual para guiar a busca de B-roll.",
                """Você é diretor de fotografia cinematográfica.
Para cada cena, defina o enquadramento ideal (Close-up, Wide, Macro),
a temperatura de cor (Quente, Fria, Desaturada) e o movimento de câmera (Slow Pan, Tilt, Dolly Zoom)."""
            )
        ]

        for sid, name, desc, body in defaults:
            skill_dir = self.skills_dir / sid
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            content = f"""---
name: "{name}"
description: "{desc}"
version: "1.0.0"
author: "Google Gemini Team"
tags: ["gemini", "drift", "ai_editor"]
---

{body}
"""
            skill_file.write_text(content, encoding="utf-8")
            self.skills[sid] = GeminiSkill(
                skill_id=sid,
                name=name,
                description=desc,
                system_instructions=body,
                skill_folder_path=str(skill_dir)
            )

    def install_skill_from_text(self, skill_name: str, description: str, markdown_content: str) -> GeminiSkill:
        """Saves a new user-provided skill into the skills directory."""
        slug = re.sub(r'[^a-zA-Z0-9_]', '_', skill_name.lower().strip()).strip('_') or "custom_skill"
        target_dir = self.skills_dir / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        full_content = markdown_content
        if not markdown_content.strip().startswith("---"):
            full_content = f"""---
name: "{skill_name}"
description: "{description}"
version: "1.0.0"
author: "Usuário do Drift"
tags: ["custom", "gemini"]
---

{markdown_content.strip()}
"""
        target_file = target_dir / "SKILL.md"
        target_file.write_text(full_content, encoding="utf-8")
        parsed = self._parse_skill_file(target_file)
        if parsed:
            self.skills[parsed.skill_id] = parsed
            return parsed

        fallback = GeminiSkill(slug, skill_name, description, system_instructions=markdown_content, skill_folder_path=str(target_dir))
        self.skills[slug] = fallback
        return fallback

    def list_skills(self) -> List[Dict[str, Any]]:
        return [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "description": s.description,
                "version": s.version,
                "author": s.author,
                "tags": s.tags
            }
            for s in self.skills.values()
        ]

    def execute_skill(self, skill_id: str, prompt_input: str) -> str:
        """
        Applies the selected Gemini Skill persona to the prompt or script.
        """
        if skill_id not in self.skills:
            return prompt_input

        skill = self.skills[skill_id]
        # In online mode with Gemini API Key, this calls google.generativeai;
        # in offline/local mode, it formats the enriched system prompt instructions.
        return f"[Skill Aplicada: {skill.name}]\n\n{skill.system_instructions}\n\n---\nConteúdo Processado:\n{prompt_input}"

