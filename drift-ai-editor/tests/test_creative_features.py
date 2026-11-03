import unittest
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from editing.layer_compositor import LayerCompositor, LayerType, BlendMode
from analysis.emotional_curve import EmotionalCurveEngine, NarrativeArcPhase
from extensions.base import BaseAiExtension, ExtensionManifest, ExtensionType
from extensions.registry import ExtensionRegistry
from voice.pronunciation_lexicon import PronunciationLexicon
from models.scene_plan import Scene

class DummyTtsExtension(BaseAiExtension):
    @property
    def manifest(self) -> ExtensionManifest:
        return ExtensionManifest(
            extension_id="dummy_tts",
            extension_type=ExtensionType.TTS,
            name="Dummy Local TTS",
            version="1.0.0",
            author="Drift AI",
            description="Mock voice engine for tests"
        )

    def is_available(self) -> bool:
        return True

    def execute(self, task: str, payload: dict) -> dict:
        return {"audio_path": "/fake/voice.wav", "duration": 4.5}

class TestCreativeFeatures(unittest.TestCase):

    def test_layer_compositor(self):
        composite = LayerCompositor.compose_scene(
            scene_order=1,
            duration_sec=6.0,
            background_media_path="D:/media/bg.mp4",
            title_text="O PODER DO FOCO",
            include_lower_third=True,
            particle_overlay_path="D:/media/dust.mov"
        )
        self.assertEqual(len(composite.layers), 3)
        self.assertEqual(composite.layers[0].layer_type, LayerType.BACKGROUND)
        self.assertEqual(composite.layers[1].blend_mode, BlendMode.SCREEN)
        self.assertEqual(composite.layers[2].layer_type, LayerType.LOWER_THIRD)
        self.assertEqual(composite.layers[2].content_text, "O PODER DO FOCO")

        # Swap background
        LayerCompositor.replace_background(composite, "D:/media/new_bg.mp4")
        self.assertEqual(composite.layers[0].source_path, "D:/media/new_bg.mp4")
        # Ensure title layer was untouched
        self.assertEqual(composite.layers[2].content_text, "O PODER DO FOCO")

    def test_emotional_curve_engine(self):
        scenes = [
            Scene(order=1, narration_text="Você acha que controla tudo? Pense de novo."),
            Scene(order=2, narration_text="O cotidiano impõe regras e tarefas intermináveis."),
            Scene(order=3, narration_text="Mas a luta interior é o que realmente define a dor."),
            Scene(order=4, narration_text="E a verdade fundamental finalmente se revela."),
            Scene(order=5, narration_text="Em paz, você encontra o silêncio e a liberdade.")
        ]
        modulations = EmotionalCurveEngine.plot_curve(scenes)
        self.assertEqual(len(modulations), 5)

        # Scene 1 must be Hook / Curiosity
        self.assertEqual(modulations[0].arc_phase, NarrativeArcPhase.HOOK_CURIOSITY)
        # Scene 4 has climax indicators ("verdade fundamental finalmente") -> Climax Revelation
        self.assertEqual(modulations[3].arc_phase, NarrativeArcPhase.CLIMAX_REVELATION)
        self.assertGreater(modulations[3].energy_level, 0.8)
        # Scene 5 must be Contemplation / Outro
        self.assertEqual(modulations[4].arc_phase, NarrativeArcPhase.CONTEMPLATION_OUTRO)

    def test_extension_registry(self):
        reg = ExtensionRegistry()
        ext = DummyTtsExtension()
        reg.register(ext)

        active = reg.get_active(ExtensionType.TTS)
        self.assertIsNotNone(active)
        self.assertEqual(active.manifest.extension_id, "dummy_tts")

        res = active.execute("synthesize", {"text": "Olá mundo"})
        self.assertEqual(res["duration"], 4.5)

        ext_list = reg.list_extensions(ExtensionType.TTS)
        self.assertEqual(len(ext_list), 1)
        self.assertTrue(ext_list[0]["is_active"])

    def test_pronunciation_lexicon(self):
        with tempfile.TemporaryDirectory() as td:
            lexicon_file = Path(td) / "lexicon.json"
            lex = PronunciationLexicon(storage_path=lexicon_file)
            lex.add_rule("Nietzsche", "Nit-che")
            lex.add_rule("Heidegger", "Ráideguer")

            raw_text = "Como dizia Nietzsche e Heidegger, a angústia é real."
            fixed_text = lex.apply_to_text(raw_text)
            self.assertIn("Nit-che", fixed_text)
            self.assertIn("Ráideguer", fixed_text)
            self.assertNotIn("Nietzsche", fixed_text)

if __name__ == "__main__":
    unittest.main()

