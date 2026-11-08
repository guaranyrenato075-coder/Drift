import random
from typing import List, Dict, Any, Optional

class ScriptGenerator:
    """
    Generates structured video scripts based on topics, languages (pt, it, de, en), and formats:
    - shorts (30-60s)
    - standard (3-5 minutes)
    - documentary (10-20 minutes)
    - mega_doc (20-60+ minutes)
    """

    TEMPLATES = {
        "pt": {
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
            ]
        },
        "it": {
            "estoicismo": [
                ("Non puoi controllare tutto ciò che accade intorno a te.", "Persona che osserva una tempesta attraverso la finestra.", ["tempesta", "pioggia", "finestra"], ["rain", "storm", "window"]),
                ("Ma puoi controllare esattamente come reagisci a ogni singolo evento.", "Persona serena che cammina all'alba nella natura.", ["meditazione", "natura", "riflessione"], ["calm", "meditation", "sunrise"]),
                ("La pace interiore comincia quando smetti di lottare contro l'incontrollabile.", "Acqua calma di un lago che riflette le montagne.", ["lago", "montagna", "pace"], ["lake", "mountain", "peace"]),
                ("Concentrati oggi su ciò che è in tuo potere e trasforma la tua mente.", "Persona che respira profondamente con sguardo sicuro.", ["focus", "respiro", "fiducia"], ["focus", "confidence", "breathing"])
            ],
            "tecnologia": [
                ("L'intelligenza artificiale sta trasformando radicalmente il modo in cui viviamo e creiamo.", "Linee di codice e luci a fibra ottica in un server moderno.", ["tecnologia", "codice", "dati"], ["code", "technology", "datacenter"]),
                ("Compiti che prima richiedevano settimane vengono ora completati in pochi secondi.", "Mani agili che operano su un'interfaccia olografica futuristica.", ["futuro", "computer", "velocita"], ["future", "computer", "interface"]),
                ("Il vero segreto non è sostituire l'uomo, ma amplificare il suo potenziale creativo.", "Designer al lavoro su visualizzazioni immersive in 3D.", ["creativita", "design", "innovazione"], ["creative", "design", "innovation"]),
                ("Il futuro non è qualcosa che aspettiamo: è ciò che stiamo costruendo oggi.", "Città intelligente illuminata di notte con veicoli autonomi.", ["citta", "futuro", "innovazione"], ["smart city", "future", "night lights"])
            ],
            "universo": [
                ("Nel silenzio del cosmo, ci sono più stelle che granelli di sabbia su tutta la Terra.", "Galassia a spirale che ruota nello spazio profondo.", ["galassia", "spazio", "stelle"], ["galaxy", "space", "nebula"]),
                ("Ogni elemento nel tuo corpo è stato forgiato nel cuore pulsante di antiche stelle.", "Supernova brillante che esplode diffondendo luce nello spazio.", ["supernova", "universo", "stelle"], ["supernova", "explosion", "universe"]),
                ("Noi siamo il modo in cui l'universo stesso osserva e comprende se stesso.", "Telescopio monumentale sotto una cupola stellata nel deserto.", ["telescopio", "cielo", "stelle"], ["telescope", "starry sky", "desert"]),
                ("Guarda il cielo stasera e ricorda quanto sia straordinaria la tua esistenza.", "Silhouette di persona che contempla la Via Lattea di notte.", ["via lattea", "notte", "cosmo"], ["milky way", "night sky", "silhouette"])
            ]
        },
        "de": {
            "estoicismo": [
                ("Du kannst nicht alles kontrollieren, was um dich herum geschieht.", "Eine Person beobachtet einen heftigen Sturm durch ein großes Fenster.", ["sturm", "regen", "fenster"], ["rain", "storm", "window"]),
                ("Aber du hast die volle Kontrolle darüber, wie du auf jedes Ereignis reagierst.", "Eine gelassene Person spaziert bei Sonnenaufgang durch den Wald.", ["meditation", "natur", "sonnenaufgang"], ["calm", "meditation", "sunrise"]),
                ("Innerer Frieden beginnt in dem Moment, in dem du aufhörst, gegen das Unvermeidbare zu kämpfen.", "Ruhiges Bergsee-Wasser spiegelt die Gipfel wider.", ["bergsee", "ruhe", "natur"], ["lake", "mountain", "peace"]),
                ("Konzentriere dich heute auf das Machbare und transformiere deinen Geist.", "Eine Person atmet tief durch und blickt entschlossen in die Ferne.", ["fokus", "vertrauen", "atmung"], ["focus", "confidence", "breathing"])
            ],
            "tecnologia": [
                ("Künstliche Intelligenz transformiert die Art und Weise, wie wir leben und kreieren.", "Serverraum mit leuchtenden Glasfasern und Datenströmen.", ["technologie", "code", "daten"], ["code", "technology", "datacenter"]),
                ("Aufgaben, die einst Wochen dauerten, werden nun in Sekunden automatisiert.", "Hände bedienen eine futuristische Benutzeroberfläche in Hochgeschwindigkeit.", ["zukunft", "computer", "tempo"], ["future", "computer", "interface"]),
                ("Das wahre Ziel ist nicht der Ersatz des Menschen, sondern die Entfesselung seiner Kreativität.", "Kreativer Entwickler arbeitet mit 3D-Hologrammen.", ["kreativitaet", "design", "innovation"], ["creative", "design", "innovation"]),
                ("Die Zukunft ist nicht etwas, worauf wir warten – wir gestalten sie jetzt.", "Intelligente Megacity bei Nacht mit autonomen Fahrzeugen.", ["stadt", "zukunft", "lichter"], ["smart city", "future", "night lights"])
            ],
            "universo": [
                ("In der Stille des Kosmos existieren mehr Sterne als Sandkörner auf der gesamten Erde.", "Eine gewaltige Spiralgalaxie rotiert im tiefen Weltall.", ["galaxie", "weltall", "sterne"], ["galaxy", "space", "nebula"]),
                ("Jedes chemische Element in deinem Körper wurde im Herzen uralter Sterne geschmiedet.", "Leuchtende Supernova explodiert im interstellaren Raum.", ["supernova", "universum", "explosion"], ["supernova", "explosion", "universe"]),
                ("Wir sind der Weg, auf dem das Universum sich selbst erforscht und versteht.", "Riesiges Teleskop unter dem funkelnden Nachthimmel in der Wüste.", ["teleskop", "himmel", "sterne"], ["telescope", "starry sky", "desert"]),
                ("Blicke heute Nacht in den Himmel und erkenne, wie außergewöhnlich deine Existenz ist.", "Silhouette einer Person, die staunend die Milchstraße betrachtet.", ["milchstrasse", "nacht", "sterne"], ["milky way", "night sky", "silhouette"])
            ]
        }
    }

    LONG_FORM_ACT_EXPANSIONS = {
        "pt": [
            ("A Origem do Enigma", "Visão panorâmica em drone estabelecendo a grandeza do cenário.", ["origem", "cenário", "abertura"], ["cinematic", "overview", "drone"]),
            ("O Primeiro Sinal de Alerta", "Câmera lenta aproximando de evidências cruciais e detalhes técnicos.", ["detalhe", "alerta", "análise"], ["macro", "investigation", "clue"]),
            ("A Virada Inesperada", "Transição veloz e iluminação dramática revelando nova perspectiva.", ["mudança", "tensão", "drama"], ["dramatic", "pivot", "shadows"]),
            ("O Ponto de Máxima Tensão", "Planos fechados e cortes intensificados destacando o clímax.", ["clímax", "pressão", "foco"], ["intensity", "crisis", "pressure"]),
            ("A Resolução e o Legado", "Iluminação dourada ao pôr do sol transmitindo encerramento triunfal.", ["triunfo", "legado", "conclusão"], ["golden hour", "resolution", "legacy"])
        ],
        "it": [
            ("L'Origine dell'Enigma", "Visione panoramica con drone che stabilisce la maestosità dello scenario.", ["origine", "scenario", "apertura"], ["cinematic", "overview", "drone"]),
            ("Il Primo Segnale d'Allarme", "Rallentatore che si avvicina a dettagli tecnici e prove cruciali.", ["dettaglio", "allarme", "analisi"], ["macro", "investigation", "clue"]),
            ("La Svolta Inaspettata", "Transizione rapida e illuminazione drammatica che rivela una nuova prospettiva.", ["svolta", "tensione", "dramma"], ["dramatic", "pivot", "shadows"]),
            ("Il Punto di Massima Tensione", "Inquadrature strette e tagli serrati che evidenziano il culmine.", ["climax", "pressione", "focus"], ["intensity", "crisis", "pressure"]),
            ("La Risoluzione e l'Eredità", "Luce dorata al tramonto che trasmette una gloriosa conclusione.", ["trionfo", "eredita", "conclusione"], ["golden hour", "resolution", "legacy"])
        ],
        "de": [
            ("Der Ursprung des Rätsels", "Panoramische Drohnenaufnahme, die die Erhabenheit der Kulisse einfängt.", ["ursprung", "kulisse", "intro"], ["cinematic", "overview", "drone"]),
            ("Das erste Warnsignal", "Zeitlupenaufnahme auf entscheidende Details und technische Spuren.", ["detail", "warnung", "analyse"], ["macro", "investigation", "clue"]),
            ("Die unerwartete Wendung", "Schneller Schnitt und dramatisches Licht offenbaren eine neue Dimension.", ["wendung", "spannung", "drama"], ["dramatic", "pivot", "shadows"]),
            ("Der Höhepunkt der Spannung", "Nahaufnahmen und beschleunigtes Pacing betonen den entscheidenden Climax.", ["climax", "druck", "fokus"], ["intensity", "crisis", "pressure"]),
            ("Die Auflösung und das Vermächtnis", "Goldene Abendsonne symbolisiert den triumphalen Abschluss.", ["triumph", "vermaechtnis", "abschluss"], ["golden hour", "resolution", "legacy"])
        ]
    }

    @classmethod
    def generate(
        cls,
        topic: str,
        duration_type: str = "shorts",
        duration_minutes: Optional[float] = None,
        language: str = "pt"
    ) -> str:
        """
        Generates a formatted script ready for ScriptSegmenter and Pipeline Planning.
        Supports languages: 'pt' (Português), 'it' (Italiano), 'de' (Deutsch), 'en' (English).
        Supports durations: 'shorts' (30s), 'standard' (3-5m), 'documentary' (10-20m) and 'mega_doc' (20-60+m).
        """
        lang_key = (language or "pt").lower()
        if lang_key not in cls.TEMPLATES:
            if lang_key in ("ita", "italian"):
                lang_key = "it"
            elif lang_key in ("deu", "ger", "german", "deutsch"):
                lang_key = "de"
            else:
                lang_key = "pt"

        lang_templates = cls.TEMPLATES.get(lang_key, cls.TEMPLATES["pt"])
        topic_lower = topic.lower()
        selected_scenes = None

        for key in lang_templates:
            if key in topic_lower or (key == "estoicismo" and any(k in topic_lower for k in ["stoisch", "stoic", "filosofia", "mind"])):
                selected_scenes = list(lang_templates[key])
                break

        if not selected_scenes:
            clean_topic = topic.strip()
            if lang_key == "it":
                selected_scenes = [
                    (f"Oggi scoprirai qualcosa di veramente affascinante su {clean_topic}.", f"Scena dinamica che introduce il tema {clean_topic}.", ["apertura", "visione"], ["cinematic", "overview"]),
                    (f"Il grande impatto di {clean_topic} sta nel modo in cui trasforma ogni cosa intorno a noi.", f"Dettagli visivi e movimento attorno a {clean_topic}.", ["dettagli", "focus"], ["focus", "details"]),
                    (f"Comprendere a fondo {clean_topic} è il primo passo per padroneggiare questa visione.", f"Persona che analizza informazioni ottenendo piena chiarezza mentale.", ["analisi", "chiarezza"], ["studying", "thinking"]),
                    (f"Applica questa conoscenza nella vita quotidiana e osserva i risultati.", f"Conclusione ispiratrice immersa nella calda luce del tramonto.", ["successo", "ispirazione"], ["sunrise", "inspiration"])
                ]
            elif lang_key == "de":
                selected_scenes = [
                    (f"Heute wirst du etwas absolut Faszinierendes über {clean_topic} entdecken.", f"Dynamische Szene, die das Thema {clean_topic} cinematisch vorstellt.", ["einfuehrung", "ueberblick"], ["cinematic", "overview"]),
                    (f"Der tiefgreifende Einfluss von {clean_topic} verändert alles um uns herum.", f"Visuelle Details und flüssige Bewegung rund um {clean_topic}.", ["fokus", "details"], ["focus", "details"]),
                    (f"{clean_topic} zu verstehen, ist der entscheidende Schritt zur Meisterschaft.", f"Person analysiert Daten und gewinnt vollkommene geistige Klarheit.", ["analyse", "klarheit"], ["studying", "thinking"]),
                    (f"Setze diese Erkenntnisse in deinem Alltag um und beobachte den Wandel.", f"Inspirierender Abschluss im goldenen Licht des Sonnenaufgangs.", ["erfolg", "inspiration"], ["sunrise", "inspiration"])
                ]
            else:
                selected_scenes = [
                    (f"Hoje você vai descobrir algo fascinante sobre {clean_topic}.", f"Cena dinâmica apresentando o tema {clean_topic}.", ["abertura", "visão"], ["cinematic", "overview"]),
                    (f"O grande impacto de {clean_topic} está na maneira como transforma tudo ao redor.", f"Detalhes visuais e movimentação em torno de {clean_topic}.", ["foco", "detalhes"], ["focus", "details"]),
                    (f"Compreender {clean_topic} é o primeiro passo para dominar esse conceito.", f"Pessoa analisando informações e obtendo clareza mental.", ["análise", "compreensão"], ["studying", "thinking"]),
                    (f"Aplique isso no seu dia a dia e veja a transformação acontecer.", f"Conclusão inspiradora com iluminação dourada do sol.", ["sucesso", "transformação"], ["sunrise", "inspiration"])
                ]

        is_mega = duration_type in ("mega_doc", "mega", "documentary") or (duration_minutes and duration_minutes >= 20.0)
        is_doc = duration_type in ("documentary", "long") or (duration_minutes and duration_minutes >= 10.0)

        act_expansions = cls.LONG_FORM_ACT_EXPANSIONS.get(lang_key, cls.LONG_FORM_ACT_EXPANSIONS["pt"])
        scenes_to_render = []

        if is_mega:
            reps = 6 if duration_type == "mega_doc" or (duration_minutes and duration_minutes >= 30) else 4
            for act_idx in range(reps):
                act_name, act_visual, pt_kw, en_kw = act_expansions[act_idx % len(act_expansions)]
                for s_idx, (base_narration, base_vis, base_pt, base_en) in enumerate(selected_scenes):
                    if lang_key == "it":
                        extended_narration = f"[Blocco {act_idx + 1} - {act_name}] {base_narration} Questo approfondisce ulteriormente l'impatto di {topic}."
                    elif lang_key == "de":
                        extended_narration = f"[Block {act_idx + 1} - {act_name}] {base_narration} Dies vertieft die Bedeutung von {topic} entscheidend."
                    else:
                        extended_narration = f"[Bloco {act_idx + 1} - {act_name}] {base_narration} Compreender isso aprofunda o impacto de {topic}."
                    
                    extended_vis = f"{act_visual} {base_vis}"
                    scenes_to_render.append((extended_narration, extended_vis, base_pt + pt_kw, base_en + en_kw))
        elif is_doc:
            for act_idx in range(3):
                act_name, act_visual, pt_kw, en_kw = act_expansions[act_idx % len(act_expansions)]
                for base_narration, base_vis, base_pt, base_en in selected_scenes:
                    scenes_to_render.append((f"{act_name}: {base_narration}", f"{act_visual} {base_vis}", base_pt, base_en))
        else:
            scenes_to_render = selected_scenes

        label_scene = "SCENA" if lang_key == "it" else ("SZENE" if lang_key == "de" else "CENA")
        label_narr = "NARRAZIONE" if lang_key == "it" else ("SPRECHERTEXT" if lang_key == "de" else "NARRAÇÃO")
        label_vis = "DESCRIZIONE VISIVA" if lang_key == "it" else ("VISUELLE BESCHREIBUNG" if lang_key == "de" else "DESCRIÇÃO VISUAL")
        label_dur = "DURATA: automatica" if lang_key == "it" else ("DAUER: automatisch" if lang_key == "de" else "DURAÇÃO: automática")

        lines: List[str] = []
        for idx, (narration, visual, pt_kws, en_kws) in enumerate(scenes_to_render, 1):
            lines.append(f"{label_scene} {idx:02d}")
            lines.append(f"{label_narr}: {narration}")
            lines.append(f"{label_vis}: {visual}")
            lines.append(label_dur)
            lines.append("")

        return "\n".join(lines)
