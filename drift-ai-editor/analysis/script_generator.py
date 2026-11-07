import random
from typing import List, Dict, Any, Optional

class ScriptGenerator:
    """
    Generates structured video scripts based on topics and formats:
    - shorts (30-60s)
    - standard (3-5 minutes)
    - documentary (10-20 minutes)
    - mega_doc (20-60+ minutes)
    """

    TEMPLATES = {
        "estoicismo": [
            ("Você não controla tudo o que acontece ao seu redor.", "Pessoa observando tempestade forte pela janela.", ["chuva", "tempestade", "janela"], ["rain", "storm", "window"]),
            ("Mas pode controlar com precisão como você reage a cada evento.", "Pessoa serena caminhando ao amanhecer em meio à natureza.", ["meditação", "reflexão", "natureza"], ["calm", "meditation", "sunrise"]),
            ("A paz interior começa no momento em que você para de lutar contra o incontrolável.", "Água calma de um lago refletindo montanhas.", ["lago", "montanha", "reflexo"], ["lake", "mountain", "peace"]),
            ("Foque hoje no que está sob o seu alcance e transforme sua mente.", "Pessoa respirando fundo e sorrindo confiante.", ["foco", "confiança", "respiração"], ["focus", "confidence", "breathing"])
        ],
        "tecnologia": [
            ("A inteligência artificial está transformando a forma como criamos e vivemos.", "Linhas de código e luzes de fibra ótica em servidor moderno.", ["código", "tecnologia", "dados"], ["code", "technology", "datacenter"]),
            ("Tarefas que antes levavam semanas agora são automatizadas em segundos.", "Mãos ágeis operando interface futurista em alta velocidade.", ["futuro", "computador", "velocidade"], ["future", "computer", "interface"]),
            ("O segredo não é substituir o ser humano, mas amplificar o potencial criativo.", "Designer trabalhando com visualizações holográficas 3D.", ["criatividade", "design", "inovação"], ["creative", "design", "innovation"]),
            ("O futuro não é algo que esperamos. É algo que estamos construindo agora.", "Cidade inteligente com carros autônomos e luzes noturnas.", ["cidade", "inteligente", "futuro"], ["smart city", "future", "night lights"])
        ],
        "universo": [
            ("No silêncio do cosmos, existem mais estrelas do que grãos de areia em toda a Terra.", "Galáxia espiral girando no espaço profundo com nebulosas.", ["galáxia", "espaço", "estrelas"], ["galaxy", "space", "nebula"]),
            ("Cada elemento químico no seu corpo foi forjado no coração de estrelas antigas.", "Supernova brilhante explodindo e espalhando luz pelo espaço.", ["supernova", "explosão", "universo"], ["supernova", "explosion", "universe"]),
            ("Somos a maneira pela qual o próprio universo reflete e compreende a si mesmo.", "Telescópio gigante sob um céu estrelado no deserto.", ["telescópio", "céu", "estrelas"], ["telescope", "starry sky", "desert"]),
            ("Olhe para o céu hoje e lembre-se do quão extraordinária é a sua existência.", "Pessoa observando a Via Láctea em noite clara.", ["via láctea", "noite", "observação"], ["milky way", "night sky", "silhouette"])
        ],
        "produtividade": [
            ("O segredo dos realizadores não é a motivação diária, mas o poder dos sistemas.", "Relógio de precisão funcionando com engrenagens em movimento.", ["relógio", "tempo", "precisão"], ["clock", "gears", "time"]),
            ("Pequenas vitórias consistentes constroem resultados que parecem impossíveis.", "Atleta treinando no primeiro raio de sol da manhã.", ["treino", "disciplina", "amanhecer"], ["workout", "discipline", "sunrise"]),
            ("Elimine as distrações e dedique blocos de foco total às suas prioridades.", "Mesa de trabalho minimalista com café e caderno organizado.", ["organização", "foco", "estudo"], ["minimalist", "workspace", "focus"]),
            ("Faça hoje o que o seu futuro eu agradecerá por ter começado.", "Pessoa subindo escadas com determinação e postura ereta.", ["sucesso", "crescimento", "conquista"], ["success", "stairs", "achievement"])
        ]
    }

    LONG_FORM_ACT_EXPANSIONS = [
        ("A Origem do Enigma", "Visão panorâmica em drone estabelecendo a grandeza do cenário.", ["origem", "cenário", "abertura"], ["cinematic", "overview", "drone"]),
        ("O Primeiro Sinal de Alerta", "Câmera lenta aproximando de evidências cruciais e detalhes técnicos.", ["detalhe", "alerta", "análise"], ["macro", "investigation", "clue"]),
        ("A Virada Inesperada", "Transição veloz e iluminação dramática revelando nova perspectiva.", ["mudança", "tensão", "drama"], ["dramatic", "pivot", "shadows"]),
        ("O Ponto de Máxima Tensão", "Planos fechados e cortes intensificados destacando o clímax.", ["clímax", "pressão", "foco"], ["intensity", "crisis", "pressure"]),
        ("A Resolução e o Legado", "Iluminação dourada ao pôr do sol transmitindo encerramento triunfal.", ["triunfo", "legado", "conclusão"], ["golden hour", "resolution", "legacy"])
    ]

    @classmethod
    def generate(cls, topic: str, duration_type: str = "shorts", duration_minutes: Optional[float] = None) -> str:
        """
        Generates a formatted script ready for ScriptSegmenter and Pipeline Planning.
        Supports: 'shorts' (30s), 'standard' (3-5m), 'documentary' (10-20m) and 'mega_doc' (20-60+m).
        """
        topic_lower = topic.lower()
        selected_scenes = None

        for key in cls.TEMPLATES:
            if key in topic_lower:
                selected_scenes = list(cls.TEMPLATES[key])
                break

        if not selected_scenes:
            clean_topic = topic.strip()
            selected_scenes = [
                (f"Hoje você vai descobrir algo fascinante sobre {clean_topic}.", f"Cena dinâmica apresentando o tema {clean_topic}.", ["abertura", "visão"], ["cinematic", "overview"]),
                (f"O grande impacto de {clean_topic} está na maneira como transforma tudo ao redor.", f"Detalhes visuais e movimentação em torno de {clean_topic}.", ["foco", "detalhes"], ["focus", "details"]),
                (f"Compreender {clean_topic} é o primeiro passo para dominar esse conceito.", f"Pessoa analisando informações e obtendo clareza mental.", ["análise", "compreensão"], ["studying", "thinking"]),
                (f"Aplique isso no seu dia a dia e veja a transformação acontecer.", f"Conclusão inspiradora com iluminação dourada do sol.", ["sucesso", "transformação"], ["sunrise", "inspiration"])
            ]

        # Multi-Duration Expansion
        is_mega = duration_type in ("mega_doc", "mega", "documentary") or (duration_minutes and duration_minutes >= 20.0)
        is_doc = duration_type in ("documentary", "long") or (duration_minutes and duration_minutes >= 10.0)

        scenes_to_render = []
        if is_mega:
            # Expande para mega documentário (ex: 20-30+ cenas base no script)
            reps = 6 if duration_type == "mega_doc" or (duration_minutes and duration_minutes >= 30) else 4
            for act_idx in range(reps):
                act_name, act_visual, pt_kw, en_kw = cls.LONG_FORM_ACT_EXPANSIONS[act_idx % len(cls.LONG_FORM_ACT_EXPANSIONS)]
                for s_idx, (base_narration, base_vis, base_pt, base_en) in enumerate(selected_scenes):
                    extended_narration = f"[Bloco {act_idx + 1} - {act_name}] {base_narration} Compreender isso aprofunda o impacto de {topic}."
                    extended_vis = f"{act_visual} {base_vis}"
                    scenes_to_render.append((extended_narration, extended_vis, base_pt + pt_kw, base_en + en_kw))
        elif is_doc:
            # 10 a 20 minutos (~12-16 cenas no script base)
            for act_idx in range(3):
                act_name, act_visual, pt_kw, en_kw = cls.LONG_FORM_ACT_EXPANSIONS[act_idx % len(cls.LONG_FORM_ACT_EXPANSIONS)]
                for base_narration, base_vis, base_pt, base_en in selected_scenes:
                    scenes_to_render.append((f"{act_name}: {base_narration}", f"{act_visual} {base_vis}", base_pt, base_en))
        else:
            # Shorts ou Padrão (3-4 cenas)
            scenes_to_render = selected_scenes

        lines: List[str] = []
        for idx, (narration, visual, pt_kws, en_kws) in enumerate(scenes_to_render, 1):
            lines.append(f"CENA {idx:02d}")
            lines.append(f"NARRAÇÃO: {narration}")
            lines.append(f"DESCRIÇÃO VISUAL: {visual}")
            lines.append(f"DURAÇÃO: automática")
            lines.append("")

        return "\n".join(lines)
