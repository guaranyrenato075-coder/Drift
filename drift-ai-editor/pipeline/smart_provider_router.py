"""
Smart Provider Router for CutWire Drift AI.
Dynamically re-orders and prioritizes the 75 media providers based on the semantic theme
of the scene narration, visual description, and keywords (e.g. Astronomy, Classical Art,
Wildlife, Culinary, Historical Archives, Modern Tech, and Cinematic B-Roll).
"""
import re
from typing import List, Dict, Set, Any, Optional
from core.lazy_provider_registry import LazyProviderRegistry

class SmartProviderRouter:
    """
    Intelligent thematic router for media providers.
    Directs scene search queries to the most specialized global providers first.
    """

    THEMATIC_CLUSTERS: Dict[str, Dict[str, Any]] = {
        "space_astronomy": {
            "tokens": {"space", "espaço", "universo", "galaxy", "galáxia", "estrela", "star", "planet", "planeta",
                       "terra", "earth", "moon", "lua", "mars", "marte", "nebula", "nebulosa", "cosmos", "astronaut",
                       "astronauta", "telescope", "telescópio", "physics", "física", "quantum", "cern", "nasa", "esa"},
            "priority": ["nasa", "esa", "cern", "unsplash", "pexels", "pixabay", "flickr_commons", "wikimedia"]
        },
        "history_antiquity_philosophy": {
            "tokens": {"filosofia", "philosophy", "estoico", "stoic", "sêneca", "marcus aurelius", "marco aurélio",
                       "epicteto", "epictetus", "roma", "rome", "grécia", "greece", "egypt", "egito", "renascença",
                       "renaissance", "medieval", "sculpture", "escultura", "museum", "museu", "painting", "pintura",
                       "antiquity", "antiguidade", "emperor", "imperador", "gladiator", "gladiador", "knight", "cavaleiro"},
            "priority": ["harvard_art", "met_museum", "walters_art", "nga", "yale", "artic", "mauritshuis",
                         "british_library", "smk", "paris_musees", "mia", "old_book_illustrations", "cleveland_art"]
        },
        "historical_documentary_archive": {
            "tokens": {"war", "guerra", "world war", "segunda guerra", "soldier", "soldado", "army", "exército",
                       "vintage", "retro", "1900", "1920", "1930", "1940", "1950", "1960", "president", "presidente",
                       "revolution", "revolução", "speech", "discurso", "broadcast", "documentary", "documentário",
                       "cold war", "guerra fria", "civil rights", "direitos civis", "history", "história"},
            "priority": ["nara", "aapb", "prelinger", "loc", "dpla", "trove", "flickr_commons", "wikimedia", "archive_org", "dvids"]
        },
        "food_culinary": {
            "tokens": {"food", "comida", "culinária", "cozinha", "chef", "cooking", "cozinhando", "recipe", "receita",
                       "coffee", "café", "espresso", "bakery", "padaria", "restaurant", "restaurante", "gourmet",
                       "dish", "prato", "breakfast", "café da manhã", "dinner", "jantar", "dessert", "sobremesa",
                       "fruit", "fruta", "vegetable", "legumes", "wine", "vinho"},
            "priority": ["foodiesfeed", "pexels", "pixabay", "unsplash", "kaboompics", "picjumbo", "barnimages"]
        },
        "nature_wildlife_geology": {
            "tokens": {"nature", "natureza", "wildlife", "animal", "animais", "bird", "pássaro", "águia", "eagle",
                       "bear", "urso", "wolf", "lobo", "forest", "floresta", "mountain", "montanha", "river", "rio",
                       "ocean", "oceano", "sea", "mar", "waterfall", "cachoeira", "lake", "lago", "canyon", "geology",
                       "geologia", "volcano", "vulcão", "park", "parque", "yellowstone", "safari", "conservation"},
            "priority": ["nps", "usfws", "noaa", "usgs", "biodiversity", "skitterphoto", "goodfreephotos", "magdeleine",
                         "dareful", "coverr", "unsplash", "pexels"]
        },
        "business_tech_workspace": {
            "tokens": {"technology", "tecnologia", "computer", "computador", "laptop", "code", "código", "programming",
                       "programação", "software", "ai", "ia", "artificial intelligence", "startup", "office", "escritório",
                       "business", "negócios", "finance", "finanças", "money", "dinheiro", "investment", "investimento",
                       "crypto", "marketing", "work", "trabalho", "developer", "programador"},
            "priority": ["foca_stock", "burst", "reshot", "picjumbo", "pexels", "pixabay", "unsplash", "stockvault"]
        },
        "cinematic_moody_travel": {
            "tokens": {"cinematic", "cinematográfico", "drone", "aéreo", "aerial", "travel", "viagem", "landscape",
                       "paisagem", "sunset", "pôr do sol", "sunrise", "amanhecer", "fog", "neblina", "road", "estrada",
                       "city", "cidade", "night", "noite", "lights", "luzes", "architecture", "arquitetura", "urban",
                       "street", "rua", "motion", "movimento", "timelapse", "dark", "moody", "minimalist", "minimalista"},
            "priority": ["magdeleine", "splitshire", "lifeofpix", "videezy", "videvo", "mazwai", "dareful", "coverr",
                         "mixkit", "jay_mantri", "barnimages", "iso_republic", "pexels"]
        },
        "creative_quirky_hooks": {
            "tokens": {"crazy", "maluco", "funny", "engraçado", "weird", "estranho", "surprise", "surpresa",
                       "shocking", "chocante", "curiosity", "curiosidade", "mystery", "mistério", "hook", "viral",
                       "humor", "creative", "criativo"},
            "priority": ["gratisography", "reshot", "pexels", "pixabay", "unsplash"]
        }
    }

    # Fallback default general order
    DEFAULT_GENERAL_ORDER = [
        "pexels", "pixabay", "unsplash", "coverr", "mixkit", "dareful", "videvo",
        "videezy", "openverse", "wikimedia"
    ]

    @classmethod
    def classify_cluster(cls, text: str) -> Optional[str]:
        """
        Identifies the primary semantic category cluster for a given text query or scene context.
        """
        words = set(re.findall(r'[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ0-9_-]+', text.lower()))
        best_cluster = None
        max_matches = 0
        for cat_name, cat_data in cls.THEMATIC_CLUSTERS.items():
            matches = len(words.intersection(cat_data["tokens"]))
            if matches > max_matches:
                max_matches = matches
                best_cluster = cat_name
        return best_cluster

    @classmethod
    def route_providers(cls, keywords: List[str], text: str = "") -> List[str]:
        """
        Determines the optimal provider priority order for the given context.
        Returns all 75 available provider keys, sorted with the best matching providers first.
        """
        all_available = LazyProviderRegistry.available_providers()
        all_set = set(all_available)

        # Normalize text and extract search tokens
        combined = " ".join(keywords).lower() + " " + text.lower()
        words = set(re.findall(r'[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ0-9_-]+', combined))

        scored_categories: List[tuple[str, int]] = []
        for cat_name, cat_data in cls.THEMATIC_CLUSTERS.items():
            match_count = len(words.intersection(cat_data["tokens"]))
            if match_count > 0:
                scored_categories.append((cat_name, match_count))

        scored_categories.sort(key=lambda x: x[1], reverse=True)

        prioritized: List[str] = []
        seen: Set[str] = set()

        # Add top matched category providers
        for cat_name, _ in scored_categories:
            for p in cls.THEMATIC_CLUSTERS[cat_name]["priority"]:
                if p in all_set and p not in seen:
                    prioritized.append(p)
                    seen.add(p)

        # Add default general providers next
        for p in cls.DEFAULT_GENERAL_ORDER:
            if p in all_set and p not in seen:
                prioritized.append(p)
                seen.add(p)

        # Append all remaining providers to ensure complete 100% catalog coverage
        for p in all_available:
            if p not in seen:
                prioritized.append(p)
                seen.add(p)

        return prioritized
