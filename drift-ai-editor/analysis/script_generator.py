import random
from typing import List, Dict, Any

class ScriptGenerator:
    """
    Generates structured video scripts based on topics and formats (Shorts 9:16 or Long 16:9).
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

    @classmethod
    def generate(cls, topic: str, duration_type: str = "shorts") -> str:
        """
        Generates a formatted script ready for ScriptSegmenter.
        """
        topic_lower = topic.lower()
        selected_scenes = None

        for key in cls.TEMPLATES:
            if key in topic_lower:
                selected_scenes = cls.TEMPLATES[key]
                break

        if not selected_scenes:
            # Fallback dynamic script based on topic words
            clean_topic = topic.strip()
            selected_scenes = [
                (f"Hoje você vai descobrir algo fascinante sobre {clean_topic}.", f"Cena dinâmica apresentando o tema {clean_topic}.", ["abertura", "visão"], ["cinematic", "overview"]),
                (f"O grande impacto de {clean_topic} está na maneira como transforma tudo ao redor.", f"Detalhes visuais e movimentação em torno de {clean_topic}.", ["foco", "detalhes"], ["focus", "details"]),
                (f"Compreender {clean_topic} é o primeiro passo para dominar esse conceito.", f"Pessoa analisando informações e obtendo clareza mental.", ["análise", "compreensão"], ["studying", "thinking"]),
                (f"Aplique isso no seu dia a dia e veja a transformação acontecer.", f"Conclusão inspiradora com iluminação dourada do sol.", ["sucesso", "transformação"], ["sunrise", "inspiration"])
            ]

        # If shorts, keep 3 or 4 scenes (approx 30s)
        lines: List[str] = []
        for idx, (narration, visual, pt_kws, en_kws) in enumerate(selected_scenes, 1):
            lines.append(f"CENA {idx:02d}")
            lines.append(f"NARRAÇÃO: {narration}")
            lines.append(f"DESCRIÇÃO VISUAL: {visual}")
            lines.append(f"DURAÇÃO: automática")
            lines.append("")

        return "\n".join(lines)

