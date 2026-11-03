import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from models.scene_plan import MediaCandidate

class SemanticLocalSearch:
    """
    Local Semantic Search Engine:
    Maps natural phrases (e.g. 'homem caminhando sozinho na chuva', 'planeta visto do espaço')
    into semantic visual concept vectors, matching files based on thematic clusters,
    visual tags, subfolder taxonomy, and contextual synonyms without cloud exposure.
    """

    CONCEPT_TAXONOMY = {
        "space": ["universo", "espaço", "planeta", "terra", "lua", "galáxia", "estrela", "astronauta", "cosmos", "nebula", "orbit", "space", "planet", "stars"],
        "rain_solitude": ["chuva", "chovendo", "caminhando", "sozinho", "solitário", "rua", "guarda-chuva", "tempestade", "rain", "walking", "alone", "storm", "wet"],
        "nature_calm": ["floresta", "árvores", "mata", "rio", "lago", "montanha", "amanhecer", "pôr do sol", "natureza", "forest", "trees", "lake", "sunset", "mountain"],
        "decision_ponder": ["homem", "pessoa", "olhando", "janela", "pensando", "hesitando", "dúvida", "decisão", "silhueta", "man", "thinking", "window", "shadow", "ponder"],
        "technology": ["computador", "dados", "futuro", "robô", "inteligência", "rede", "digital", "código", "tech", "computer", "data", "cyber", "ai"]
    }

    def __init__(self, catalog_entries: Optional[List[Dict[str, Any]]] = None):
        self.catalog = catalog_entries or []

    def load_from_indexer(self, indexer_catalog: List[Dict[str, Any]]):
        self.catalog = indexer_catalog

    def extract_semantic_tags(self, text: str) -> set:
        clean_text = text.lower()
        matched_tags = set()
        for concept, tokens in self.CONCEPT_TAXONOMY.items():
            if any(tok in clean_text for tok in tokens):
                matched_tags.add(concept)
                matched_tags.update(tokens)
        # Also include raw words of 3+ letters
        raw_words = re.findall(r'[a-zA-ZáéíóúãõçÁÉÍÓÚÃÕÇ]{3,}', clean_text)
        matched_tags.update(w.lower() for w in raw_words)
        return matched_tags

    def search_by_meaning(
        self,
        query: str,
        media_type: str = "all",
        limit: int = 4
    ) -> List[MediaCandidate]:
        """
        Matches user's natural conceptual phrase against the local indexed library
        using semantic overlap and concept cluster weighting.
        """
        query_tags = self.extract_semantic_tags(query)
        if not query_tags or not self.catalog:
            return []

        scored_results = []
        for item in self.catalog:
            if media_type != "all" and item.get("type") != media_type:
                continue

            file_tags = set(item.get("keywords", []))
            # Also extract tags from path
            path_tags = self.extract_semantic_tags(item.get("path", "") + " " + item.get("filename", ""))
            all_file_tags = file_tags.union(path_tags)

            # Calculate semantic overlap
            intersection = query_tags.intersection(all_file_tags)
            if intersection:
                score = len(intersection) * 10
                # Extra weight for exact keyword match
                for t in query_tags:
                    if t in item.get("filename", "").lower():
                        score += 15
                scored_results.append((score, item))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        candidates: List[MediaCandidate] = []
        for score, item in scored_results[:limit]:
            cand = MediaCandidate(
                platform="local",
                external_id=Path(item["path"]).stem,
                title=f"Arquivo Local: {item['filename']}",
                preview_url=item["path"],
                download_url=item["path"],
                local_cached_path=item["path"],
                creator="Acervo Pessoal",
                page_url=f"file:///{item['path']}",
                license="Acervo Próprio (Livre)",
                width=1920,
                height=1080,
                duration=item.get("duration", 8.0) if item.get("type") == "video" else 4.0,
                aspect_ratio="16:9",
                score=float(score)
            )
            candidates.append(cand)

        return candidates

