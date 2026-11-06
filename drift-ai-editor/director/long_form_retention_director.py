"""
Long-Form Video Retention Director for CutWire Drift AI.
Implements cognitive tension curves, three-act pacing, and automatic pattern interrupts
(micro-retention hooks) every 3 to 4 minutes for 10-30+ minute documentaries and long-form videos.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import math
from models.scene_plan import Scene, SceneState

@dataclass
class RetentionHook:
    scene_order: int
    minute_mark: float
    hook_type: str            # 'curiosity_gap', 'counter_intuitive', 'dramatic_pivot', 'stakes_escalation'
    suggested_phrase: str
    pacing_action: str        # 'accelerate_cuts', 'deep_pause', 'sound_riser', 'visual_punch'

@dataclass
class LongFormPacingStructure:
    total_scenes: int
    estimated_duration_sec: float
    acts: List[Dict[str, Any]]
    hooks_inserted: List[RetentionHook]
    retention_score: float    # 0 to 100

class LongFormRetentionDirector:
    """
    Analyzes long script scene sequences and strategically injects retention hooks
    and narrative pacing milestones to maximize YouTube Watch Time.
    """

    DEFAULT_HOOK_LIBRARY = {
        "curiosity_gap": [
            "Mas o que parecia ser o desfecho revelou algo que ninguém esperava.",
            "Antes de ver o resultado, um detalhe crucial passou despercebido por quase todos.",
            "O que aconteceu a seguir mudou para sempre a rota dessa história.",
            "Para compreender o impacto real, precisamos olhar para onde ninguém estava olhando."
        ],
        "counter_intuitive": [
            "Ao contrário do que a maioria das pessoas acredita, a verdade é o oposto exato.",
            "A resposta comum para essa pergunta está completamente errada. Veja por quê.",
            "O que parece uma fraqueza óbvia é, na verdade, a maior vantagem oculta.",
            "Por mais bizarro que pareça, quanto mais tentavam evitar, mais aceleravam o processo."
        ],
        "dramatic_pivot": [
            "E foi exatamente aqui que tudo começou a ruir.",
            "Em uma única fração de segundo, a situação tomou um rumo sem volta.",
            "Nenhum plano resiste ao inesperado, e este foi o ponto de virada definitivo.",
            "Quando todos pensavam que a tempestade havia passado, o verdadeiro teste começou."
        ],
        "stakes_escalation": [
            "Agora a aposta não era apenas o sucesso, mas a sobrevivência do projeto.",
            "O risco atingiu um patamar onde um único erro custaria absolutamente tudo.",
            "Não havia mais espaço para recuo: era tudo ou nada a partir deste momento.",
            "As consequências desse momento continuam ecoando até os dias de hoje."
        ]
    }

    @classmethod
    def structure_narrative_arc(
        cls,
        scenes: List[Scene],
        target_interval_sec: float = 210.0  # Gancho a cada 3.5 minutos (210s)
    ) -> LongFormPacingStructure:
        if not scenes:
            return LongFormPacingStructure(
                total_scenes=0,
                estimated_duration_sec=0.0,
                acts=[],
                hooks_inserted=[],
                retention_score=0.0
            )

        # 1. Calcula a linha de tempo cumulativa
        timeline_sec = 0.0
        scene_times = []
        for s in scenes:
            dur = s.duration if s.duration > 0 else 6.0
            scene_times.append((s, timeline_sec, dur))
            timeline_sec += dur

        total_duration = timeline_sec
        total_mins = total_duration / 60.0

        # 2. Divide em 3 Atos Dramáticos
        # Ato 1: 0% a 25% (Introdução, Conflito Inicial)
        # Ato 2: 25% a 75% (Desenvolvimento, Escalada, Revelações)
        # Ato 3: 75% a 100% (Clímax e Conclusão / Resolução)
        act1_end = total_duration * 0.25
        act2_end = total_duration * 0.75

        acts = [
            {
                "act_number": 1,
                "name": "O Mistério & A Promessa",
                "start_sec": 0.0,
                "end_sec": round(act1_end, 1),
                "mood": "suspense",
                "tempo": "moderate_building"
            },
            {
                "act_number": 2,
                "name": "A Escalada de Tensão & Conflito",
                "start_sec": round(act1_end, 1),
                "end_sec": round(act2_end, 1),
                "mood": "investigative_tense",
                "tempo": "dynamic_varying"
            },
            {
                "act_number": 3,
                "name": "O Clímax & A Grande Lição",
                "start_sec": round(act2_end, 1),
                "end_sec": round(total_duration, 1),
                "mood": "climactic_inspiring",
                "tempo": "intense_then_reflective"
            }
        ]

        # 3. Detecta os marcos de inserção de ganchos (a cada target_interval_sec)
        hooks_inserted: List[RetentionHook] = []
        hook_types = ["curiosity_gap", "counter_intuitive", "dramatic_pivot", "stakes_escalation"]
        
        next_checkpoint = target_interval_sec
        hook_idx = 0

        for sc, cur_time, dur in scene_times:
            if cur_time + dur >= next_checkpoint and next_checkpoint < total_duration - 45.0:
                h_type = hook_types[hook_idx % len(hook_types)]
                library = cls.DEFAULT_HOOK_LIBRARY[h_type]
                phrase = library[(hook_idx // len(hook_types)) % len(library)]
                
                hooks_inserted.append(RetentionHook(
                    scene_order=sc.order,
                    minute_mark=round(cur_time / 60.0, 2),
                    hook_type=h_type,
                    suggested_phrase=phrase,
                    pacing_action="visual_punch" if h_type == "dramatic_pivot" else "deep_pause"
                ))

                hook_idx += 1
                next_checkpoint += target_interval_sec

        # 4. Cálculo de Score de Retenção Estimado (0 a 100)
        # Vídeos sem ganchos longos perdem retenção progressivamente
        base_score = 65.0
        bonus_hooks = min(len(hooks_inserted) * 7.5, 30.0)
        scene_density = len(scenes) / max(1.0, total_mins)
        density_bonus = 5.0 if 8.0 <= scene_density <= 20.0 else 0.0 # Ritmo ideal: 8 a 20 cortes/minuto

        retention_score = min(100.0, round(base_score + bonus_hooks + density_bonus, 1))

        return LongFormPacingStructure(
            total_scenes=len(scenes),
            estimated_duration_sec=round(total_duration, 1),
            acts=acts,
            hooks_inserted=hooks_inserted,
            retention_score=retention_score
        )

    @classmethod
    def apply_hooks_to_scenes(cls, scenes: List[Scene], target_interval_sec: float = 210.0) -> List[Scene]:
        """
        Enriches matching scenes with pattern interrupt hooks and visual directors.
        """
        pacing = cls.structure_narrative_arc(scenes, target_interval_sec)
        hook_map = {h.scene_order: h for h in pacing.hooks_inserted}

        for sc in scenes:
            if sc.order in hook_map:
                h = hook_map[sc.order]
                # Prefixa ou enriquece a fala se ainda não possuir gancho
                if not sc.narration_text.startswith(h.suggested_phrase[:20]):
                    sc.narration_text = f"{h.suggested_phrase} {sc.narration_text}".strip()
                sc.keywords.append(f"hook:{h.hook_type}")
                sc.keywords.append(f"action:{h.pacing_action}")

        return scenes
