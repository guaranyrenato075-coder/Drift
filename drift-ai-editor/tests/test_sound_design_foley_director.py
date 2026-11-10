import unittest
from models.scene_plan import ProjectPlan, Scene
from audio.sound_design_foley_director import SoundDesignFoleyAutoDirector


class TestSoundDesignFoleyAutoDirector(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="O Segredo Financeiro",
            scenes=[
                Scene(order=1, narration_text="Existe um segredo perigoso que nunca contaram.", duration=4.0),
                Scene(order=2, narration_text="Eles ganharam milhões de dólares com esse método.", duration=5.0),
                Scene(order=3, narration_text="Clique aqui no link para ver mais.", duration=3.0)
            ]
        )

    def test_get_foley_categories(self):
        cats = SoundDesignFoleyAutoDirector.get_foley_categories()
        self.assertIn("transitions", cats)
        self.assertIn("impacts", cats)

    def test_generate_foley_cues(self):
        res = SoundDesignFoleyAutoDirector.generate_foley_cues(self.plan)
        self.assertGreater(res["total_cues"], 0)
        cues = res["cues"]
        # Verifica se há transição nos cortes
        transition_cues = [c for c in cues if c["type"] == "transition"]
        self.assertEqual(len(transition_cues), 2)  # Entre cena 1->2 e 2->3
        # Verifica se detectou palavra-chave de impacto "segredo" ou "perigo"
        impact_cues = [c for c in cues if c["type"] == "impact"]
        self.assertGreaterEqual(len(impact_cues), 1)


if __name__ == "__main__":
    unittest.main()
