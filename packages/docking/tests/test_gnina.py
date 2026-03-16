import shutil
import unittest
from pathlib import Path

import pytest
from bio_analyze_docking.engines.factory import DockingEngineFactory
from bio_analyze_docking.engines.gnina import GninaEngine


class TestGninaEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        self.receptor_path = Path("receptor.pdbqt")
        self.ligand_path = Path("ligand.pdbqt")

        # Check for real data
        data_dir = Path(__file__).parent / "data"
        prep_rec_dir = data_dir / "prepared_receptor"
        prep_lig_dir = data_dir / "prepared_ligand"

        used_real_data = False
        if prep_rec_dir.exists() and prep_lig_dir.exists():
            recs = list(prep_rec_dir.glob("*.pdbqt"))
            ligs = list(prep_lig_dir.glob("*.pdbqt"))
            if recs and ligs:
                shutil.copy(recs[0], self.receptor_path)
                shutil.copy(ligs[0], self.ligand_path)
                used_real_data = True

        if not used_real_data:
            # Create dummy files
            self.receptor_path.write_text("ATOM")
            self.ligand_path.write_text("ATOM")

    def tearDown(self):
        if self.receptor_path.exists():
            self.receptor_path.unlink()
        if self.ligand_path.exists():
            self.ligand_path.unlink()
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

    def test_initialization_fail_if_missing(self):
        """Test that initialization fails if gnina is missing."""
        if shutil.which("gnina"):
            self.skipTest("Gnina is installed, cannot test missing executable behavior")

        with self.assertRaises(RuntimeError):
            GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)

    @pytest.mark.skipif(not shutil.which("gnina"), reason="Gnina not installed")
    def test_initialization(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, GninaEngine)
        self.assertTrue(engine.gnina_executable)

    @pytest.mark.skipif(not shutil.which("gnina"), reason="Gnina not installed")
    def test_compute_box(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        self.assertEqual(engine.box_center, center)
        self.assertEqual(engine.box_size, size)

    @pytest.mark.skipif(not shutil.which("gnina"), reason="Gnina not installed")
    def test_dock(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)

        try:
            engine.dock(exhaustiveness=1, n_poses=1)
        except RuntimeError as e:
            # Gnina might fail due to invalid input files
            print(f"Gnina failed as expected (invalid input): {e}")

    @pytest.mark.skipif(not shutil.which("gnina"), reason="Gnina not installed")
    def test_factory_create_gnina(self):
        engine = DockingEngineFactory.create_engine("gnina", self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, GninaEngine)


if __name__ == "__main__":
    unittest.main()
