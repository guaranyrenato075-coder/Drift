"""
Multi-Format Simultaneous Exporter for CutWire Drift AI.
Compiles render pipelines for Landscape (16:9 1920x1080), Vertical (9:16 1080x1920),
and Square (1:1 1080x1080) in a single unified export pass.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple
import os

class AspectTarget(str, Enum):
    LANDSCAPE_16_9 = "16:9"   # YouTube / Desktop (1920x1080)
    VERTICAL_9_16 = "9:16"     # Shorts / TikTok / Reels (1080x1920)
    SQUARE_1_1 = "1:1"         # Instagram Feed / LinkedIn (1080x1080)

@dataclass
class TargetFormatRenderSpec:
    target: AspectTarget
    width: int
    height: int
    output_filename: str
    ffmpeg_scale_filter: str

@dataclass
class MultiFormatBatchJob:
    project_id: str
    base_title: str
    output_directory: str
    specs: List[TargetFormatRenderSpec]

class MultiFormatExporter:
    """
    Coordinates multi-platform delivery without requiring separate manual project timelines.
    """

    @classmethod
    def prepare_multiformat_batch(
        cls,
        project_id: str,
        title: str,
        output_dir: str = "output/deliveries"
    ) -> MultiFormatBatchJob:
        clean_title = title.lower().replace(" ", "_")

        specs = [
            TargetFormatRenderSpec(
                target=AspectTarget.LANDSCAPE_16_9,
                width=1920,
                height=1080,
                output_filename=f"{clean_title}_16x9_youtube.mp4",
                ffmpeg_scale_filter="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            ),
            TargetFormatRenderSpec(
                target=AspectTarget.VERTICAL_9_16,
                width=1080,
                height=1920,
                output_filename=f"{clean_title}_9x16_shorts.mp4",
                ffmpeg_scale_filter="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            ),
            TargetFormatRenderSpec(
                target=AspectTarget.SQUARE_1_1,
                width=1080,
                height=1080,
                output_filename=f"{clean_title}_1x1_square.mp4",
                ffmpeg_scale_filter="scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080"
            )
        ]

        return MultiFormatBatchJob(
            project_id=project_id,
            base_title=title,
            output_directory=output_dir,
            specs=specs
        )

