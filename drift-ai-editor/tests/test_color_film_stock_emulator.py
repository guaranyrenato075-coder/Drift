import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.color_film_stock_emulator import AutoColorToneFilmStockEmulator


class TestColorFilmStockEmulator(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Filme Noir Teste",
            scenes=[
                Scene(order=1, narration_text="Uma noite chuvosa na cidade.", duration=5.0)
            ]
        )

    def test_get_available_film_stocks(self):
        stocks = AutoColorToneFilmStockEmulator.get_available_film_stocks()
        self.assertIn("kodak_vision3_5219", stocks)
        self.assertIn("fujifilm_eterna", stocks)
        self.assertIn("technicolor_3strip", stocks)
        self.assertIn("bleach_bypass", stocks)
        self.assertIn("cinema_noir", stocks)

    def test_build_ffmpeg_film_stock_filter(self):
        filter_str = AutoColorToneFilmStockEmulator.build_ffmpeg_film_stock_filter("cinema_noir", grain_intensity=1.0)
        self.assertIn("hue=s=0", filter_str)
        self.assertIn("noise=alls=", filter_str)

    def test_apply_film_stock_to_plan(self):
        res = AutoColorToneFilmStockEmulator.apply_film_stock_to_plan(self.plan, "kodak_vision3_5219", grain_intensity=0.8)
        self.assertEqual(res["status"], "APPLIED")
        self.assertEqual(self.plan.color_film_stock, "kodak_vision3_5219")
        self.assertTrue(hasattr(self.plan, "film_stock_ffmpeg_filter"))
        self.assertIn("curves=", self.plan.film_stock_ffmpeg_filter)


if __name__ == "__main__":
    unittest.main()
