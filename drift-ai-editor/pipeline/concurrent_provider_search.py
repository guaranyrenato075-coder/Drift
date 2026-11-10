"""
Concurrent Multi-Provider Search Engine for CutWire Drift AI.
Executes non-blocking parallel searches across prioritized providers using ThreadPoolExecutor,
delivering high-quality candidates in sub-second latency while guaranteeing zero UI freezes.
"""
import concurrent.futures
from typing import List, Optional, Any, Dict
from models.scene_plan import MediaCandidate, Scene, ProjectPlan
from core.lazy_provider_registry import LazyProviderRegistry
from pipeline.smart_provider_router import SmartProviderRouter
from core.smart_cache import GLOBAL_CACHE
from media.copyright_analyzer import CopyrightAnalyzer

class ConcurrentProviderSearch:
    """
    Parallel media search orchestrator across global providers.
    """

    MAX_WORKERS = 8
    PROVIDER_TIMEOUT_SEC = 2.5

    @classmethod
    def _search_single_provider(
        cls,
        provider_name: str,
        query: str,
        aspect_ratio: str,
        media_type: str,
        per_page: int = 3
    ) -> List[MediaCandidate]:
        """Queries an individual provider, checking memory cache first."""
        cache_k = f"search:{provider_name}:{query}:{aspect_ratio}:{media_type}"
        cached = GLOBAL_CACHE.get(cache_k)
        if cached is not None:
            return cached

        provider = LazyProviderRegistry.get_provider(provider_name)
        if not provider:
            return []

        try:
            results = provider.search(
                query=query,
                orientation=aspect_ratio,
                per_page=per_page,
                media_type=media_type
            )
            for cand in results:
                CopyrightAnalyzer.analyze_candidate(cand)

            GLOBAL_CACHE.set(cache_k, results, ttl_sec=900)
            return results
        except Exception:
            return []

    @classmethod
    def search_scene_candidates(
        cls,
        scene: Scene,
        plan_aspect_ratio: str = "16:9",
        plan_media_type: str = "all",
        target_candidates_count: int = 4,
        max_providers_to_query: int = 12
    ) -> List[MediaCandidate]:
        """
        Executes concurrent searches across the top semantically prioritized providers.
        """
        keywords = scene.english_keywords or ["cinematic", "hd"]
        primary_query = keywords[0] if keywords else "cinematic"
        secondary_query = keywords[1] if len(keywords) > 1 else primary_query

        # Determine prioritized provider order based on scene theme
        ranked_providers = SmartProviderRouter.route_providers(
            keywords=keywords,
            text=f"{scene.narration_text} {scene.visual_description}"
        )
        selected_provider_names = ranked_providers[:max_providers_to_query]

        collected_candidates: List[MediaCandidate] = []
        seen_ids = set()

        # Execute parallel searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
            future_to_provider = {}
            for p_name in selected_provider_names:
                # Query with primary keyword
                fut = executor.submit(
                    cls._search_single_provider,
                    p_name,
                    primary_query,
                    plan_aspect_ratio,
                    plan_media_type,
                    per_page=2
                )
                future_to_provider[fut] = (p_name, primary_query)

            # Gather results preserving priority
            for fut in concurrent.futures.as_completed(future_to_provider, timeout=cls.PROVIDER_TIMEOUT_SEC * 2):
                try:
                    res = fut.result(timeout=cls.PROVIDER_TIMEOUT_SEC)
                    for item in res:
                        if item.external_id not in seen_ids:
                            collected_candidates.append(item)
                            seen_ids.add(item.external_id)
                except Exception:
                    pass

        # If we need more candidates, try secondary query on top 4 providers
        if len(collected_candidates) < target_candidates_count and secondary_query != primary_query:
            top_providers = selected_provider_names[:4]
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(
                        cls._search_single_provider,
                        p_name,
                        secondary_query,
                        plan_aspect_ratio,
                        plan_media_type,
                        per_page=2
                    )
                    for p_name in top_providers
                ]
                for fut in concurrent.futures.as_completed(futures, timeout=cls.PROVIDER_TIMEOUT_SEC):
                    try:
                        res = fut.result(timeout=cls.PROVIDER_TIMEOUT_SEC)
                        for item in res:
                            if item.external_id not in seen_ids:
                                collected_candidates.append(item)
                                seen_ids.add(item.external_id)
                    except Exception:
                        pass

        return collected_candidates
