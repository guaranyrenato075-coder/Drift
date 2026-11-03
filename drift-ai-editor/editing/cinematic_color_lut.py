"""
Cinematic Color Grading & Mood LUT Director for CutWire Drift AI.
Harmonizes disparate stock media assets using unified color science profiles
(Teal & Orange, Vintage 35mm, Bleach Bypass, Cyberpunk Neon, Noir B&W)
and generates robust FFmpeg color grading filter strings.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class ColorMoodProfile(str, Enum):
    TEAL_AND_ORANGE = "teal_and_orange"     # Hollywood blockbuster contrast
    VINTAGE_35MM = "vintage_35mm"           # Warm nostalgic film emulation
    BLEACH_BYPASS = "bleach_bypass"         # Gritty war/documentary high contrast
    CYBERPUNK_NEON = "cyberpunk_neon"       # Deep shadows with cyan and magenta accents
    NOIR_MONOCHROME = "noir_monochrome"     # High-contrast dramatic black and white
    NATURAL_REC709 = "natural_rec709"       # Clean neutral broadcast standard

@dataclass
class ColorGradeRecipe:
    mood: ColorMoodProfile
    saturation: float  # 1.0 = normal
    contrast: float    # 1.0 = normal
    gamma: float       # 1.0 = normal
    color_balance_r: float
    color_balance_g: float
    color_balance_b: float
    ffmpeg_filter: str

class CinematicColorLutDirector:
    """
    Applies unified color treatment across diverse footage to ensure cohesive visual aesthetics.
    """

    PRESETS: Dict[ColorMoodProfile, Dict] = {
        ColorMoodProfile.TEAL_AND_ORANGE: {
            "sat": 1.25, "contrast": 1.15, "gamma": 0.95,
            "r": 0.12, "g": -0.02, "b": -0.10,
            "desc": "Teal and orange complementary color contrast"
        },
        ColorMoodProfile.VINTAGE_35MM: {
            "sat": 0.90, "contrast": 1.05, "gamma": 1.08,
            "r": 0.08, "g": 0.05, "b": -0.06,
            "desc": "Warm film stock with gentle shadow rolloff"
        },
        ColorMoodProfile.BLEACH_BYPASS: {
            "sat": 0.60, "contrast": 1.35, "gamma": 0.90,
            "r": 0.0, "g": 0.0, "b": 0.0,
            "desc": "Desaturated, gritty silver retention look"
        },
        ColorMoodProfile.CYBERPUNK_NEON: {
            "sat": 1.40, "contrast": 1.20, "gamma": 0.92,
            "r": 0.05, "g": -0.08, "b": 0.15,
            "desc": "Deep cool shadows with saturated neon highlights"
        },
        ColorMoodProfile.NOIR_MONOCHROME: {
            "sat": 0.0, "contrast": 1.30, "gamma": 0.95,
            "r": 0.0, "g": 0.0, "b": 0.0,
            "desc": "Pure black and white with high dramatic tonal range"
        },
        ColorMoodProfile.NATURAL_REC709: {
            "sat": 1.0, "contrast": 1.0, "gamma": 1.0,
            "r": 0.0, "g": 0.0, "b": 0.0,
            "desc": "Neutral standard Rec.709 profile"
        }
    }

    @classmethod
    def get_color_recipe(cls, mood: ColorMoodProfile = ColorMoodProfile.TEAL_AND_ORANGE) -> ColorGradeRecipe:
        p = cls.PRESETS.get(mood, cls.PRESETS[ColorMoodProfile.NATURAL_REC709])
        sat = p["sat"]
        contrast = p["contrast"]
        gamma = p["gamma"]
        r = p["r"]
        g = p["g"]
        b = p["b"]

        eq_filter = f"eq=saturation={sat}:contrast={contrast}:gamma={gamma}"
        cb_filter = f"colorbalance=rs={r}:gs={g}:bs={b}" if (r != 0 or g != 0 or b != 0) else ""

        full_filter = f"{eq_filter},{cb_filter}".strip(",")

        return ColorGradeRecipe(
            mood=mood,
            saturation=sat,
            contrast=contrast,
            gamma=gamma,
            color_balance_r=r,
            color_balance_g=g,
            color_balance_b=b,
            ffmpeg_filter=full_filter
        )

