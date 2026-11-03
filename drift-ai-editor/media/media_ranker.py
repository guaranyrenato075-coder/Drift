from typing import List, Dict, Any, Optional
from models.scene_plan import MediaCandidate, Scene

class MediaRanker:
    """
    Ranks, scores, and filters media candidates to curate a diverse 4-option gallery
    per scene, penalizing repeated creators, repetitive platforms, and mismatched resolutions.
    """

    @staticmethod
    def score_candidate(
        candidate: MediaCandidate,
        scene: Scene,
        used_creators: List[str],
        used_external_ids: List[str],
        preferred_aspect: str = "16:9"
    ) -> float:
        """
        Calculates a ranking score (0.0 to 100.0) based on resolution, duration,
        aspect ratio match, and uniqueness.
        """
        score = 50.0

        # Penalize already used items to prevent duplicate scenes across the video
        if candidate.external_id in used_external_ids:
            return 0.0

        # Penalize repeated creators to ensure aesthetic diversity
        if candidate.creator in used_creators:
            score -= 20.0

        # Resolution score
        if candidate.width >= 3840 or candidate.height >= 2160:
            score += 25.0  # 4K
        elif candidate.width >= 1920 or candidate.height >= 1080:
            score += 15.0  # 1080p Full HD
        elif candidate.width >= 1280:
            score += 5.0
        else:
            score -= 15.0  # Sub-HD penalty

        # Aspect ratio match
        cand_aspect = candidate.aspect_ratio
        if preferred_aspect == "16:9" and cand_aspect in ("16:9", "landscape"):
            score += 15.0
        elif preferred_aspect == "9:16" and cand_aspect in ("9:16", "portrait"):
            score += 15.0
        elif preferred_aspect == "1:1" and cand_aspect == "1:1":
            score += 15.0
        else:
            score -= 5.0

        # Duration suitability (only for video clips)
        if candidate.duration > 0:
            target_dur = scene.duration or 4.0
            if candidate.duration >= target_dur:
                score += 10.0
            else:
                score -= 10.0  # Needs looping or freeze frame

        # Platform credibility bonus
        if candidate.platform in ("pexels", "coverr", "unsplash", "nasa"):
            score += 5.0

        return max(0.0, min(100.0, score))

    @classmethod
    def rank_scene_candidates(
        cls,
        candidates: List[MediaCandidate],
        scene: Scene,
        used_creators: List[str],
        used_external_ids: List[str],
        preferred_aspect: str = "16:9",
        limit: int = 4
    ) -> List[MediaCandidate]:
        """
        Returns top scored candidates (alternatives gallery) sorted highest-to-lowest,
        ensuring diversity.
        """
        if not candidates:
            return []

        scored = []
        for c in candidates:
            s = cls.score_candidate(c, scene, used_creators, used_external_ids, preferred_aspect)
            scored.append((s, c))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Select diverse top candidates (try not to pick identical platforms)
        chosen: List[MediaCandidate] = []
        seen_platforms = set()

        # Pass 1: pick diverse platforms
        for score, cand in scored:
            if score <= 0.0:
                continue
            if cand.platform not in seen_platforms:
                chosen.append(cand)
                seen_platforms.add(cand.platform)
            if len(chosen) >= limit:
                break

        # Pass 2: fill remaining slots from top scores
        if len(chosen) < limit:
            for score, cand in scored:
                if score <= 0.0:
                    continue
                if cand not in chosen:
                    chosen.append(cand)
                if len(chosen) >= limit:
                    break

        return chosen

