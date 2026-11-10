"""
AI Voice Emotion & Inflection Director for CutWire Drift AI.
Applies context-aware expressive prosody, pitch modulation, and dynamic speech rate adjustments
per scene to eliminate flat robotic narration and elevate vocal drama.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class VoiceInflectionPreset:
    scene_order: int
    narrative_mood: str  # "misterioso", "urgente_climax", "reflexivo", "solene_conclusao"
    speed_factor: float  # 0.90 to 1.15
    pitch_adjustment_hz: str  # "-5Hz", "+10Hz", etc.
    volume_gain_db: float
    breath_pause_sec: float
    ssml_prosody_snippet: str

class AIVoiceEmotionInflectionDirector:
    """
    Directs emotional inflection parameters for neural TTS engines.
    """

    @classmethod
    def evaluate_scene_mood(cls, scene: Scene, total_scenes: int) -> str:
        text = (scene.narration_text or "").lower()

        if scene.order == 1:
            return "misterioso"
        elif scene.order == total_scenes:
            return "solene_conclusao"
        elif any(k in text for k in ["perigo", "choque", "urgente", "explosão", "morte", "rápido", "confronto"]):
            return "urgente_climax"
        elif any(k in text for k in ["filosofia", "pense", "tempo", "silêncio", "compreender", "significa"]):
            return "reflexivo"
        return "neutro_engajado"

    @classmethod
    def calculate_scene_inflection(cls, scene: Scene, mood: str) -> VoiceInflectionPreset:
        if mood == "misterioso":
            speed = 0.94
            pitch = "-4Hz"
            vol = -0.5
            pause = 0.45
            prosody = f'<prosody rate="-6%" pitch="-4Hz">{scene.narration_text}</prosody>'
        elif mood == "urgente_climax":
            speed = 1.08
            pitch = "+8Hz"
            vol = 1.5
            pause = 0.20
            prosody = f'<prosody rate="+8%" pitch="+8Hz" volume="+2dB">{scene.narration_text}</prosody>'
        elif mood == "solene_conclusao":
            speed = 0.92
            pitch = "-2Hz"
            vol = 0.0
            pause = 0.60
            prosody = f'<prosody rate="-8%" pitch="-2Hz">{scene.narration_text}</prosody>'
        elif mood == "reflexivo":
            speed = 0.96
            pitch = "-1Hz"
            vol = -1.0
            pause = 0.50
            prosody = f'<prosody rate="-4%" pitch="-1Hz">{scene.narration_text}</prosody>'
        else:
            speed = 1.00
            pitch = "+0Hz"
            vol = 0.0
            pause = 0.30
            prosody = f'<prosody rate="0%" pitch="0Hz">{scene.narration_text}</prosody>'

        return VoiceInflectionPreset(
            scene_order=scene.order,
            narrative_mood=mood,
            speed_factor=speed,
            pitch_adjustment_hz=pitch,
            volume_gain_db=vol,
            breath_pause_sec=pause,
            ssml_prosody_snippet=prosody
        )

    @classmethod
    def direct_project_voice_inflections(cls, plan: ProjectPlan) -> Dict[str, Any]:
        inflections: List[VoiceInflectionPreset] = []
        total = len(plan.scenes)

        for s in plan.scenes:
            mood = cls.evaluate_scene_mood(s, total)
            inf = cls.calculate_scene_inflection(s, mood)
            inflections.append(inf)

        return {
            "project_id": plan.project_id,
            "total_scenes_directed": len(inflections),
            "inflections": [i.__dict__ for i in inflections]
        }
