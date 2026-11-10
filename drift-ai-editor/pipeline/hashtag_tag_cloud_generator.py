"""
AI Hashtag & SEO Tag Cloud Generator for CutWire Drift AI.
Extracts high-ranking keywords, niche-specific hashtags, and 500-character YouTube Studio tags
from scene transcripts and visual descriptions to maximize search indexing and recommendation algorithms.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Set
import re
from models.scene_plan import ProjectPlan

@dataclass
class SeoMetadataPackage:
    project_id: str
    niche_category: str
    hashtags: List[str]
    formatted_hashtags_string: str
    youtube_tags_string: str
    long_tail_keywords: List[str]

class AIHashtagTagCloudGenerator:
    """
    Generates optimized search metadata and hashtags for video publishing.
    """

    STOPWORDS = {
        "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
        "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "sob", "sobre",
        "que", "e", "ou", "se", "como", "mas", "mais", "muito", "este", "esta", "isto",
        "the", "of", "and", "in", "to", "for", "with", "on", "at", "by", "from", "is"
    }

    NICHE_CLUSTERS = {
        "Ciência & Astronomia": ["espaço", "universo", "galáxia", "estrela", "nasa", "planeta", "ciência", "física", "cosmos"],
        "História & Civilizações": ["história", "império", "século", "roma", "antigo", "guerra", "rei", "filosofia", "civilização"],
        "Curiosidades & Mistérios": ["mistério", "segredo", "estranho", "desconhecido", "fato", "verdade", "curiosidade", "incrível"],
        "Tecnologia & Futuro": ["tecnologia", "futuro", "ia", "robô", "inovação", "computador", "digital", "ciência"],
        "Natureza & Vida Selvagem": ["natureza", "animal", "floresta", "selvagem", "oceano", "planeta", "vida", "terra"]
    }

    @classmethod
    def _detect_niche(cls, tokens: Set[str]) -> str:
        best_niche = "Curiosidades & Fatos Gerais"
        max_matches = 0
        for niche, kws in cls.NICHE_CLUSTERS.items():
            matches = len(tokens.intersection(set(kws)))
            if matches > max_matches:
                max_matches = matches
                best_niche = niche
        return best_niche

    @classmethod
    def generate_seo_metadata(cls, plan: ProjectPlan) -> Dict[str, Any]:
        combined_text = (plan.title + " " + " ".join(
            s.narration_text + " " + s.visual_description + " " + " ".join(s.english_keywords or [])
            for s in plan.scenes
        )).lower()

        raw_words = re.findall(r'[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ0-9_-]+', combined_text)
        tokens = [w for w in raw_words if len(w) > 3 and w not in cls.STOPWORDS]
        token_set = set(tokens)

        # Word frequency
        freq: Dict[str, int] = {}
        for w in tokens:
            freq[w] = freq.get(w, 0) + 1

        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [w[0].capitalize() for w in sorted_tokens[:15]]

        detected_niche = cls._detect_niche(token_set)

        # Hashtags
        base_hashtags = [f"#{w[0]}" for w in sorted_tokens[:8]]
        if "#Shorts" not in base_hashtags and plan.config.aspect_ratio == "9:16":
            base_hashtags.insert(0, "#Shorts")
        base_hashtags.append(f"#{detected_niche.split()[0].replace('&', '')}")
        unique_hashtags = list(dict.fromkeys(base_hashtags))

        # YouTube Studio tags (comma-separated, under 500 chars limit)
        clean_title = re.sub(r'^(projeto|video|roteiro)\s*:\s*', '', plan.title, flags=re.IGNORECASE).strip()
        tags_list = [clean_title]
        tags_list.extend(top_keywords)
        tags_list.append(detected_niche)

        # Build comma-separated string under 500 characters
        yt_tags_str = ""
        for t in tags_list:
            candidate = f"{t}, " if not yt_tags_str else f"{yt_tags_str}{t}, "
            if len(candidate) <= 490:
                yt_tags_str = candidate
            else:
                break
        yt_tags_str = yt_tags_str.rstrip(", ")

        # Long-tail query suggestions
        long_tail = [
            f"o que é {top_keywords[0].lower()}" if top_keywords else f"mistérios de {clean_title}",
            f"como funciona {top_keywords[1].lower()}" if len(top_keywords) > 1 else f"história de {clean_title}",
            f"documentário completo {clean_title}",
            f"curiosidades sobre {clean_title}"
        ]

        return {
            "project_id": plan.project_id,
            "niche_category": detected_niche,
            "hashtags": unique_hashtags,
            "formatted_hashtags_string": " ".join(unique_hashtags),
            "youtube_tags_string": yt_tags_str,
            "long_tail_keywords": long_tail
        }
