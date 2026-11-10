"""
Unit tests for ProjectPackagerZip in Drift AI.
Verifies full project archive creation, manifest bundling, and zip compression.
"""
import unittest
import tempfile
from pathlib import Path
from storage.project_packager_zip import ProjectPackagerZip, PackageArchiveResult
from models.scene_plan import ProjectPlan, Scene

class TestProjectPackagerZip(unittest.TestCase):

    def test_package_project_zip(self):
        plan = ProjectPlan(title="Projeto Arquivo Teste")
        plan.scenes = [
            Scene(order=1, narration_text="Cena teste de empacotamento.", duration=4.0)
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_zip = Path(tmp_dir) / "teste_pacote.zip"
            result = ProjectPackagerZip.package_project(plan, output_zip_path=str(target_zip))

            self.assertIsInstance(result, PackageArchiveResult)
            self.assertTrue(target_zip.exists())
            self.assertGreater(result.compressed_bytes, 0)
            self.assertGreaterEqual(result.file_count, 4)
            self.assertIn("manifesto_projeto.json", result.included_files)
            self.assertIn("roteiro_completo.txt", result.included_files)
            self.assertIn("capitulos_youtube.txt", result.included_files)
            self.assertIn("licencas_copyright.json", result.included_files)

if __name__ == "__main__":
    unittest.main()
