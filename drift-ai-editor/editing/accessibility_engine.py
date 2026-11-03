"""
Audiovisual Accessibility Engine for CutWire Drift AI.
Audits subtitle readability, WCAG 2.1 contrast compliance,
reading velocity limits (CPS/WPM), and detects narrative gaps for Audio Description (AD).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class AccessibilityAuditReport:
    total_subtitles: int
    wcag_pass_count: int
    wcag_fail_count: int
    reading_speed_violations: List[Dict]
    contrast_recommendations: List[str]
    audio_description_slots: List[Tuple[float, float]]  # (start_time, end_time)

class AccessibilityEngine:
    """
    Ensures video productions comply with modern digital accessibility standards.
    """

    MAX_RECOMMENDED_CPS = 21.0  # Max 21 characters per second for comfortable reading
    MIN_DISPLAY_DURATION = 1.2  # Min duration for single subtitle card

    @staticmethod
    def calculate_luminance(r: int, g: int, b: int) -> float:
        """Calculates relative luminance according to sRGB WCAG formula."""
        def channel_lum(c: int) -> float:
            val = c / 255.0
            return val / 12.92 if val <= 0.03928 else ((val + 0.055) / 1.055) ** 2.4
        return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

    @classmethod
    def calculate_contrast_ratio(cls, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        l1 = cls.calculate_luminance(*rgb1)
        l2 = cls.calculate_luminance(*rgb2)
        brightest = max(l1, l2)
        darkest = min(l1, l2)
        return (brightest + 0.05) / (darkest + 0.05)

    @classmethod
    def audit_subtitles(
        cls,
        subtitles: List[Dict],  # [{'text': str, 'start': float, 'end': float, 'text_rgb': (255,255,255), 'bg_rgb': (0,0,0)}]
        audio_pauses: Optional[List[Tuple[float, float]]] = None
    ) -> AccessibilityAuditReport:
        pass_count = 0
        fail_count = 0
        violations = []
        contrast_recs = []

        for idx, sub in enumerate(subtitles):
            text = sub.get("text", "").strip()
            duration = max(0.1, sub.get("end", 0.0) - sub.get("start", 0.0))
            cps = len(text) / duration

            if cps > cls.MAX_RECOMMENDED_CPS:
                violations.append({
                    "index": idx,
                    "text": text,
                    "duration": round(duration, 2),
                    "cps": round(cps, 1),
                    "issue": f"Text flashes too fast ({round(cps, 1)} CPS > {cls.MAX_RECOMMENDED_CPS} limit)"
                })

            t_rgb = sub.get("text_rgb", (255, 255, 255))
            b_rgb = sub.get("bg_rgb", (0, 0, 0))
            ratio = cls.calculate_contrast_ratio(t_rgb, b_rgb)

            if ratio >= 4.5:
                pass_count += 1
            else:
                fail_count += 1
                contrast_recs.append(
                    f"Subtitle #{idx} has insufficient contrast ratio {round(ratio, 2)}:1 (minimum 4.5:1 required)"
                )

        # Detect audio description windows in dialogue pauses > 2.5s
        ad_slots = []
        if audio_pauses:
            for start, end in audio_pauses:
                if (end - start) >= 2.5:
                    ad_slots.append((round(start, 2), round(end, 2)))

        return AccessibilityAuditReport(
            total_subtitles=len(subtitles),
            wcag_pass_count=pass_count,
            wcag_fail_count=fail_count,
            reading_speed_violations=violations,
            contrast_recommendations=contrast_recs,
            audio_description_slots=ad_slots
        )

