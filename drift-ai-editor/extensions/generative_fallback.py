"""
Generative AI Fallback Engine for CutWire Drift AI.
Detects when stock media queries have low candidate confidence or conceptual gaps,
synthesizes detailed prompts with style anchors, and invokes local image generation (ComfyUI / SD / Flux).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json

@dataclass
class GenAiRequest:
    scene_index: int
    base_concept: str
    positive_prompt: str
    negative_prompt: str
    aspect_ratio: str  # "16:9", "9:16", "1:1"
    width: int
    height: int
    steps: int = 25
    seed: int = 42

@dataclass
class GenAiResult:
    scene_index: int
    image_path: str
    generation_time_sec: float
    seed_used: int
    success: bool

class GenerativeAiFallback:
    """
    Coordinates local generative image models when stock media APIs have no matching footage.
    """

    STYLE_ENHANCERS = {
        "cinematic": "cinematic lighting, 8k resolution, shot on 35mm lens, photorealistic, dramatic atmosphere, depth of field",
        "documentary": "archival film grain, authentic historical setting, detailed textures, soft natural lighting",
        "cyberpunk": "neon lighting, reflective wet asphalt, volumetric fog, octane render, high tech futuristic details",
        "anime": "Makoto Shinkai aesthetic, vivid color palette, beautiful cloudscapes, hand-drawn anime key visual"
    }

    DEFAULT_NEGATIVE = "blurry, low quality, distorted, extra limbs, bad anatomy, text, watermark, signature, ugly"

    @classmethod
    def craft_generation_request(
        cls,
        scene_index: int,
        concept: str,
        style: str = "cinematic",
        aspect_ratio: str = "16:9"
    ) -> GenAiRequest:
        enhancer = cls.STYLE_ENHANCERS.get(style, cls.STYLE_ENHANCERS["cinematic"])
        positive = f"{concept}, {enhancer}"

        w, h = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920) if aspect_ratio == "9:16" else (1080, 1080)

        return GenAiRequest(
            scene_index=scene_index,
            base_concept=concept,
            positive_prompt=positive,
            negative_prompt=cls.DEFAULT_NEGATIVE,
            aspect_ratio=aspect_ratio,
            width=w,
            height=h,
            steps=25,
            seed=1337 + scene_index
        )

    @classmethod
    def simulate_local_render(cls, req: GenAiRequest, output_dir: str = "output/gen_media") -> GenAiResult:
        """Simulates zero-latency local fallback render generation."""
        mock_path = f"{output_dir}/gen_scene_{req.scene_index:02d}.png"
        return GenAiResult(
            scene_index=req.scene_index,
            image_path=mock_path,
            generation_time_sec=1.4,
            seed_used=req.seed,
            success=True
        )

