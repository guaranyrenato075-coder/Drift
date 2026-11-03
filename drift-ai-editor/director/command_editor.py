import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene, MediaCandidate

@dataclass
class CommandAction:
    action_type: str        # 'replace_scene_media', 'adjust_audio', 'adjust_pacing', 'change_voice', 'remove_scene', 'regenerate_scene'
    scene_order: Optional[int]
    parameters: Dict[str, Any]
    human_description: str
    requires_drift_sync: bool = True

@dataclass
class CommandPlan:
    original_prompt: str
    actions: List[CommandAction] = field(default_factory=list)
    confidence: float = 1.0
    summary_message: str = ""

class NaturalLanguageCommandEditor:
    """
    Parses conversational user instructions and translates them into precise,
    non-destructive timeline and project operations.
    Examples:
      - 'Troque a cena 2 por imagens do espaço'
      - 'Deixe a música mais baixa e narração mais alta'
      - 'Acelere o ritmo dos primeiros 20 segundos'
      - 'Mude a voz da cena 1 para voz feminina'
    """

    @classmethod
    def parse_instruction(cls, instruction: str, plan: ProjectPlan) -> CommandPlan:
        text = instruction.strip().lower()
        actions: List[CommandAction] = []

        # 1. Detect "Trocar/Mudar cena X por Y"
        replace_match = re.search(r'(?:troque|mude|substitua|altere)\s+(?:a\s+)?cena\s+(\d+)\s+por\s+(.+)', text)
        if replace_match:
            scene_num = int(replace_match.group(1))
            query_desc = replace_match.group(2).strip()
            actions.append(
                CommandAction(
                    action_type="replace_scene_media",
                    scene_order=scene_num,
                    parameters={"query": query_desc},
                    human_description=f"Buscar e substituir a mídia da Cena {scene_num} pelo tema '{query_desc}'."
                )
            )

        # 2. Detect "Música mais baixa / mais alta"
        if "música" in text or "trilha" in text or "fundo" in text:
            if "mais baixa" in text or "diminua" in text or "abaixar" in text or "volume menor" in text:
                actions.append(
                    CommandAction(
                        action_type="adjust_audio",
                        scene_order=None,
                        parameters={"track": "music", "volume_change_db": -6.0},
                        human_description="Reduzir o volume da música de fundo em -6dB para dar mais clareza à narração."
                    )
                )
            elif "mais alta" in text or "aumente" in text:
                actions.append(
                    CommandAction(
                        action_type="adjust_audio",
                        scene_order=None,
                        parameters={"track": "music", "volume_change_db": +3.0},
                        human_description="Aumentar o volume da música de fundo em +3dB."
                    )
                )

        # 3. Detect "Acelerar / Desacelerar ritmo"
        if "acelere" in text or "ritmo mais rápido" in text or "mais dinâmico" in text:
            seconds_match = re.search(r'(\d+)\s*segundos', text)
            limit_sec = float(seconds_match.group(1)) if seconds_match else None
            actions.append(
                CommandAction(
                    action_type="adjust_pacing",
                    scene_order=None,
                    parameters={"speed_factor": 1.15, "limit_seconds": limit_sec},
                    human_description=f"Acelerar o ritmo dos cortes em 15%{f' nos primeiros {limit_sec} segundos' if limit_sec else ''}."
                )
            )
        elif "mais lento" in text or "desacelere" in text or "ritmo calmo" in text:
            actions.append(
                CommandAction(
                    action_type="adjust_pacing",
                    scene_order=None,
                    parameters={"speed_factor": 0.85},
                    human_description="Diminuir o ritmo dos cortes em 15% para dar um tom mais reflexivo."
                )
            )

        # 4. Detect "Mudar voz / narração"
        voice_match = re.search(r'(?:mude|troque|use)\s+(?:a\s+)?voz(?:\s+da\s+cena\s+(\d+))?\s+para\s+([a-zA-Z0-9_\-]+)', text)
        if voice_match:
            scene_num = int(voice_match.group(1)) if voice_match.group(1) else None
            new_voice = voice_match.group(2).strip()
            actions.append(
                CommandAction(
                    action_type="change_voice",
                    scene_order=scene_num,
                    parameters={"voice_id": new_voice},
                    human_description=f"Alterar locutor para '{new_voice}'{f' apenas na Cena {scene_num}' if scene_num else ' em todo o projeto'}."
                )
            )

        # 5. Detect "Remover / Deletar cena X"
        del_match = re.search(r'(?:remova|delete|apague|retire)\s+(?:a\s+)?cena\s+(\d+)', text)
        if del_match:
            scene_num = int(del_match.group(1))
            actions.append(
                CommandAction(
                    action_type="remove_scene",
                    scene_order=scene_num,
                    parameters={},
                    human_description=f"Remover a Cena {scene_num} da timeline e reindexar as cenas seguintes."
                )
            )

        summary = f"{len(actions)} alteração(ões) identificada(s)." if actions else "Nenhuma ação automática reconhecida. Tente instruções como 'Troque a cena 1 por montanhas' ou 'Deixe a música mais baixa'."
        return CommandPlan(
            original_prompt=instruction,
            actions=actions,
            confidence=0.95 if actions else 0.2,
            summary_message=summary
        )

    @classmethod
    def apply_plan(cls, command_plan: CommandPlan, plan: ProjectPlan) -> List[str]:
        """Applies planned modifications to project plan object safely."""
        results: List[str] = []
        for action in command_plan.actions:
            if action.action_type == "replace_scene_media":
                scene = next((s for s in plan.scenes if s.order == action.scene_order), None)
                if scene:
                    new_q = action.parameters.get("query", "")
                    scene.visual_description = new_q
                    scene.english_keywords.insert(0, new_q)
                    scene.selected_media = None  # Invalidate to force re-search
                    results.append(f"Cena {scene.order}: Mídia agendada para substituição com tema '{new_q}'.")
            elif action.action_type == "adjust_audio":
                vol = action.parameters.get("volume_change_db", 0)
                results.append(f"Áudio ajustado: Música de fundo {vol:+.1f}dB.")
            elif action.action_type == "adjust_pacing":
                speed = action.parameters.get("speed_factor", 1.0)
                limit = action.parameters.get("limit_seconds")
                cur_t = 0.0
                for s in plan.scenes:
                    if limit and cur_t > limit:
                        break
                    s.duration = round((s.duration or 4.0) / speed, 2)
                    cur_t += s.duration
                results.append(f"Ritmo ajustado em {speed}x.")
            elif action.action_type == "remove_scene":
                plan.scenes = [s for s in plan.scenes if s.order != action.scene_order]
                plan.reindex_scenes()
                results.append(f"Cena {action.scene_order} removida com sucesso.")
        return results

