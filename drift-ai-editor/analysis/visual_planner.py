import re
from typing import List, Dict, Tuple
from models.scene_plan import Scene

class VisualPlanner:
    """
    Extracts semantic concepts, visual descriptions, and search keywords
    (Portuguese and English) for scenes.
    """

    # Common stopwords in Portuguese and English
    STOPWORDS = {
        # Portuguese
        "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
        "em", "no", "na", "nos", "nas", "por", "pelo", "pela", "pelos", "pelas",
        "para", "com", "sem", "sob", "sobre", "que", "se", "e", "mas", "ou", "porque",
        "como", "quando", "onde", "quem", "qual", "não", "nao", "sim", "mais", "muito",
        "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas", "aquele",
        "aquela", "aqueles", "aquelas", "seu", "sua", "seus", "suas", "meu", "minha",
        "nosso", "nossa", "ele", "ela", "eles", "elas", "você", "voce", "vocês", "voces",
        "ser", "estar", "ter", "haver", "fazer", "ir", "tudo", "nada", "algo", "pode",
        # English
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
        "by", "from", "up", "about", "into", "over", "after", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did", "can", "could",
        "will", "would", "should", "not", "no", "you", "your", "we", "our", "it", "its"
    }

    # Common semantic mappings for stock footage queries
    SEMANTIC_THEMES = [
        # --- Mitologia Grega, Antiguidade Clássica e Épicos Históricos ---
        (re.compile(r'\b(zeus|raio|trovão|trovao|olimpo|deus|deuses|olímpico|olimpico|soberano|trono)\b', re.IGNORECASE),
         "Estátua clássica de Zeus no monte Olimpo sob céu de tempestade e raios",
         ["zeus", "olimpo", "estátua grega", "raios", "mitologia"],
         ["zeus statue", "mount olympus storm", "ancient greece lightning", "classical greek sculpture", "temple of zeus", "greek mythology"]),

        (re.compile(r'\b(hécate|hecate|deusa|tríplice|triplice|encruzilhada|tocha|tochas|chama|fogo na noite|mistério|misterio|magia)\b', re.IGNORECASE),
         "Deusa Hécate em encruzilhada de pedra arcaica segurando tochas flamejantes na noite",
         ["hécate", "tocha", "noite", "encruzilhada", "estátua"],
         ["burning torch ancient ruins", "greek goddess statue torch", "ancient crossroads night", "torch flame dark night", "ancient stone temple night", "mystic ancient torch"]),

        (re.compile(r'\b(tártaro|tartaro|abismo|submundo|profundezas|sombras|escuridão|escuridao|caverna|monstro|titã|titãs|tita|titas|correntes|cinzas|fumaça)\b', re.IGNORECASE),
         "Abismo primordial do Tártaro e submundo mítico com névoa, fumaça vulcânica e rochas escuras",
         ["tártaro", "submundo", "abismo", "cinzas", "profundezas"],
         ["ancient dark underworld abyss", "volcanic fissure smoke dark", "ancient cavern fog", "underground stone crypt dark", "abyssal primordial cave", "dark volcanic rocks"]),

        (re.compile(r'\b(hesíodo|hesiodo|teogonia|poeta|escritura|pergaminho|papiro|texto|antigo|filosofia|filósofo|filosofo|mito|mitologia|história|historia)\b', re.IGNORECASE),
         "Pergaminhos antigos e papiros gregos iluminados por luz de vela em arquivo de pedra",
         ["pergaminho", "papiro grego", "filosofia", "antiguidade"],
         ["ancient greek manuscript", "ancient scroll candle", "greek marble bust", "ancient library scroll", "classical antique parchment", "ancient greek inscription"]),

        (re.compile(r'\b(grécia|grecia|templo|ruína|ruina|ruínas|ruinas|acrópole|acropole|mármore|marmore|helenístico|helenistico|arcaico|parthenon|coluna|colunas)\b', re.IGNORECASE),
         "Ruínas majestosas de templos gregos antigos e colunas de mármore clássicas sob luz dourada",
         ["templo grego", "ruínas", "acrópole", "mármore", "parthenon"],
         ["ancient greek temple columns", "acropolis athens ruins", "greek marble ruins", "delphi temple ancient greece", "ancient parthenon columns", "classical greek architecture"]),

        (re.compile(r'\b(sacrifício|sacrificio|altar|oferenda|rito|ritual|sacerdote|culto|prece|adoração|adoracao)\b', re.IGNORECASE),
         "Altar antigo de pedra com incenso e chamas rituais em santuário grego",
         ["altar", "ritual", "templo", "incenso", "santuário"],
         ["ancient stone altar smoke", "ancient temple incense flame", "greek sacrificial altar", "ancient ritual temple flame", "greek marble sanctuary"]),

        (re.compile(r'\b(mar|egeu|mediterrâneo|mediterraneo|costa|ondas|litoral|rochas|promontório)\b', re.IGNORECASE),
         "Costa rochosa do Mar Egeu com penhascos gregos e ondas dramáticas",
         ["mar egeu", "costa grega", "penhasco", "ondas"],
         ["aegean sea coast cliffs", "ancient greece coast sunset", "mediterranean rocky coast", "greek islands dramatic cliffs"]),

        # --- Temas Gerais e Modernos ---
        (re.compile(r'\b(tempestade|chuva|tempo|vento|clima)\b', re.IGNORECASE), 
         "Pessoa observando tempestade pela janela", ["chuva", "tempestade", "janela"], ["rain", "storm", "window", "thunder"]),
        (re.compile(r'\b(controla|controle|reage|reação|mente|pensamento|pensar|medita)\b', re.IGNORECASE),
         "Pessoa serena refletindo ou meditando na natureza", ["meditação", "reflexão", "mente", "calma"], ["meditation", "calm", "thinking", "nature"]),
        (re.compile(r'\b(disciplina|esforço|foco|treino|trabalho|rotina|estudo)\b', re.IGNORECASE),
         "Pessoa dedicada trabalhando ou treinando ao amanhecer", ["disciplina", "treino", "foco", "esforço"], ["workout", "discipline", "focus", "sunrise"]),
        (re.compile(r'\b(tempo|relógio|hora|futuro|passado|vida|anos)\b', re.IGNORECASE),
         "Passagem do tempo com luz solar e sombras ou relógio antigo", ["tempo", "relógio", "vida"], ["time lapse", "clock", "sunlight", "hourglass"]),
        (re.compile(r'\b(espaço|universo|estrela|planeta|galáxia|cosmos)\b', re.IGNORECASE),
         "Cena cósmica do espaço sideral com estrelas e galáxias", ["espaço", "universo", "estrelas"], ["space", "galaxy", "stars", "cosmos", "planet"]),
        (re.compile(r'\b(cidade|urbano|rua|trânsito|edifício|prédio)\b', re.IGNORECASE),
         "Movimento da cidade urbana com tráfego e luzes", ["cidade", "rua", "urbano"], ["city", "urban", "traffic", "street", "timelapse"]),
        (re.compile(r'\b(natureza|floresta|árvore|montanha|mar|oceano|rio)\b', re.IGNORECASE),
         "Paisagem natural cinematográfica com florestas ou montanhas", ["natureza", "floresta", "paisagem"], ["nature", "forest", "landscape", "mountains"]),
        (re.compile(r'\b(tecnologia|computador|código|dados|inteligência|ia)\b', re.IGNORECASE),
         "Interface tecnológica moderna com visualização de dados", ["tecnologia", "dados", "computador"], ["technology", "code", "cyberpunk", "data", "future"]),
    ]

    # Portuguese to English keyword dictionary
    TRANSLATIONS = {
        # Mitologia e Antiguidade
        "zeus": "zeus statue", "hecate": "hecate goddess", "hécate": "hecate goddess",
        "deus": "greek god statue", "deusa": "greek goddess statue", "deuses": "greek gods sculpture",
        "olimpo": "mount olympus greece", "tártaro": "tartarus underworld abyss", "tartaro": "tartarus underworld abyss",
        "submundo": "underworld dark cave", "abismo": "dark abyss", "tocha": "burning torch night",
        "tochas": "burning torches ruins", "encruzilhada": "ancient crossroads night",
        "templo": "ancient greek temple", "ruínas": "ancient greek ruins", "ruina": "ancient ruins",
        "ruinas": "ancient ruins", "mármore": "classical greek marble", "marmore": "classical greek marble",
        "estátua": "classical greek sculpture", "estatua": "classical greek sculpture",
        "titã": "ancient titan myth", "titãs": "ancient titans myth", "tita": "ancient titan myth", "titas": "ancient titans myth",
        "hesíodo": "ancient greek manuscript", "hesiodo": "ancient greek manuscript",
        "pergaminho": "ancient scroll", "papiro": "ancient papyrus", "altar": "ancient stone altar",
        "mitologia": "greek mythology", "mito": "greek myth", "grécia": "ancient greece", "grecia": "ancient greece",
        "acrópole": "acropolis athens", "acropole": "acropolis athens", "parthenon": "parthenon athens",
        # Termos gerais
        "homem": "man", "mulher": "woman", "pessoa": "person", "pessoas": "people",
        "caminhando": "walking", "olhando": "looking", "observando": "watching",
        "chuva": "rain", "tempestade": "storm", "janela": "window", "reflexão": "reflection",
        "amanhecer": "sunrise", "pôr do sol": "sunset", "noite": "night", "dia": "day",
        "mar": "sea", "oceano": "ocean", "praia": "beach", "montanha": "mountain",
        "floresta": "forest", "cidade": "city", "estrada": "road", "carro": "car",
        "estudo": "studying", "trabalho": "work", "escritório": "office", "computador": "computer",
        "livro": "book", "tempo": "time", "relógio": "clock", "foco": "focus",
        "luz": "light", "sombra": "shadow", "fogo": "fire", "água": "water",
        "céu": "sky", "nuvens": "clouds", "espaço": "space", "galáxia": "galaxy",
        "futuro": "future", "tecnologia": "technology", "mão": "hands", "rosto": "face",
        "sorriso": "smile", "olhar": "gaze", "sozinho": "alone", "pensando": "thinking",
        "viagem": "travel", "mundo": "world", "terra": "earth"
    }

    @classmethod
    def plan_scene(cls, scene: Scene) -> Scene:
        """
        Analyzes the scene's narration text and populates:
        - visual_description (if empty)
        - keywords (Portuguese)
        - english_keywords (for international stock video search APIs)
        """
        text = scene.narration_text.strip()
        if not text and not scene.visual_description.strip():
            scene.keywords = ["background", "cinematic"]
            scene.english_keywords = ["cinematic", "background"]
            return scene

        # Check semantic theme matches
        matched_desc = None
        theme_pt_kw: List[str] = []
        theme_en_kw: List[str] = []
        for pattern, desc, pt_kws, en_kws in cls.SEMANTIC_THEMES:
            if pattern.search(text) or (scene.visual_description and pattern.search(scene.visual_description)):
                if not matched_desc:
                    matched_desc = desc
                theme_pt_kw.extend(pt_kws)
                theme_en_kw.extend(en_kws)

        # Set visual description if not present
        if not scene.visual_description.strip():
            if matched_desc:
                scene.visual_description = matched_desc
            else:
                scene.visual_description = f"Cena representativa com foco em {text[:60]}"

        # Extract words from narration and visual description
        combined_text = f"{text} {scene.visual_description}".lower()
        words = re.findall(r'[a-záàâãéèêíïóôõöúçñ]+', combined_text)
        
        extracted_pt: List[str] = []
        for w in words:
            if len(w) > 3 and w not in cls.STOPWORDS and w not in extracted_pt:
                extracted_pt.append(w)

        # Merge extracted with theme keywords
        all_pt = []
        for kw in theme_pt_kw + extracted_pt:
            if kw not in all_pt:
                all_pt.append(kw)
        scene.keywords = all_pt[:6]

        # Translate to English keywords
        all_en = []
        for kw in theme_en_kw:
            if kw not in all_en:
                all_en.append(kw)

        for kw in all_pt:
            if kw in cls.TRANSLATIONS and cls.TRANSLATIONS[kw] not in all_en:
                all_en.append(cls.TRANSLATIONS[kw])

        if not all_en:
            all_en = ["cinematic", "mood", "scenery"]

        scene.english_keywords = all_en[:6]
        return scene

    @classmethod
    def plan_project(cls, scenes: List[Scene]) -> List[Scene]:
        """Plans all scenes in sequence."""
        for s in scenes:
            cls.plan_scene(s)
        return scenes

