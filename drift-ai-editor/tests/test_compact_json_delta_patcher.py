import unittest
from storage.compact_json_delta_patcher import CompactJsonDeltaPatcher


class TestCompactJsonDeltaPatcher(unittest.TestCase):
    def test_compute_and_apply_delta(self):
        # Projeto com roteiro representativo
        orig = {
            "title": "Vídeo Antigo",
            "duration": 600,
            "raw_script": "Era uma vez um roteiro longo de inteligência artificial com múltiplos parágrafos e cenas complexas... " * 30,
            "scenes": [{"order": i, "text": f"Cena {i}"} for i in range(20)]
        }
        updated = dict(orig)
        updated["title"] = "Vídeo Novo com Título Atualizado"

        delta_res = CompactJsonDeltaPatcher.compute_project_delta(orig, updated)
        self.assertEqual(delta_res["status"], "success")
        self.assertGreater(delta_res["bandwidth_and_ssd_savings_pct"], 80.0)

        applied = CompactJsonDeltaPatcher.apply_delta_patch(orig, delta_res["patches"])
        self.assertEqual(applied["title"], "Vídeo Novo com Título Atualizado")
        self.assertEqual(applied["duration"], 600)


if __name__ == "__main__":
    unittest.main()
