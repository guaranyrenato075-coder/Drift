import re
from typing import List, Dict, Any
from models.scene_plan import Scene

class AudioAligner:
    """
    Handles temporal alignment between continuous narration audio and scene segments.
    """

    @staticmethod
    def align_scenes_to_total_duration(scenes: List[Scene], total_duration: float) -> List[Scene]:
        """
        Proportionally distributes durations among scenes based on word count
        when audio is continuous or individual timestamps are missing.
        """
        if not scenes or total_duration <= 0:
            return scenes

        word_counts = [max(1, len(re.findall(r'\w+', s.narration_text))) for s in scenes]
        total_words = sum(word_counts)

        current_time = 0.0
        for idx, scene in enumerate(scenes):
            proportion = word_counts[idx] / total_words
            scene_dur = round(proportion * total_duration, 2)
            scene.start_time = round(current_time, 2)
            scene.duration = scene_dur
            scene.end_time = round(current_time + scene_dur, 2)
            current_time = scene.end_time

        # Adjust any rounding discrepancy on the last scene
        if scenes:
            scenes[-1].end_time = round(total_duration, 2)
            scenes[-1].duration = round(scenes[-1].end_time - scenes[-1].start_time, 2)

        return scenes

