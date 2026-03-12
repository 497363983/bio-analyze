import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock vina and pymol modules before importing the engine
sys.modules["vina"] = MagicMock()
sys.modules["pymol"] = MagicMock()
sys.modules["loguru"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["meeko"] = MagicMock()
sys.modules["rdkit"] = MagicMock()
sys.modules["rdkit.Chem"] = MagicMock()
sys.modules["rdkit.Chem.AllChem"] = MagicMock()
sys.modules["pdbfixer"] = MagicMock()
sys.modules["openmm"] = MagicMock()
sys.modules["openmm.app"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["gemmi"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["openpyxl"] = MagicMock()

from bio_analyze_docking.engines.factory import DockingEngineFactory
from bio_analyze_docking.engines.vina import VinaEngine


class TestVinaEngine(unittest.TestCase):
    def setUp(self):
        self.receptor_path = Path("receptor.pdbqt")
        self.ligand_path = Path("ligand.pdbqt")
        self.output_dir = Path("output")

        # Mock Path.exists and mkdir
        self.path_patcher = patch("pathlib.Path.exists")
        self.mkdir_patcher = patch("pathlib.Path.mkdir")
        self.mock_exists = self.path_patcher.start()
        self.mock_mkdir = self.mkdir_patcher.start()
        self.mock_exists.return_value = True

    def tearDown(self):
        self.path_patcher.stop()
        self.mkdir_patcher.stop()

    def test_initialization(self):
        engine = VinaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, VinaEngine)
        # Verify Vina was instantiated and setup
        engine.engine.set_receptor.assert_called_with(str(self.receptor_path))
        engine.engine.set_ligand_from_file.assert_called_with(str(self.ligand_path))

    def test_compute_box(self):
        engine = VinaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        engine.engine.compute_vina_maps.assert_called_with(center=center, box_size=size)

    def test_dock(self):
        engine = VinaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        engine.dock(exhaustiveness=16, n_poses=5, min_rmsd=2.0)
        engine.engine.dock.assert_called_with(exhaustiveness=16, n_poses=5, min_rmsd=2.0)

    def test_save_results(self):
        engine = VinaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        output_name = "results.pdbqt"
        expected_path = self.output_dir / output_name
        engine.save_results(output_name)
        engine.engine.write_poses.assert_called_with(str(expected_path), n_poses=9, overwrite=True)

    def test_score(self):
        engine = VinaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        # Mock energies return value: list of [affinity, rmsd_lb, rmsd_ub]
        engine.engine.energies.return_value = [[-8.5, 0.0, 0.0]]
        score = engine.score()
        self.assertEqual(score, -8.5)

    def test_get_all_poses_info(self):
        engine = VinaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        engine.engine.energies.return_value = [[-8.5, 0.0, 0.0], [-7.5, 1.0, 2.0]]
        info = engine.get_all_poses_info(n_poses=2)
        self.assertEqual(len(info), 2)
        self.assertEqual(info[0]["affinity"], -8.5)
        self.assertEqual(info[1]["affinity"], -7.5)


class TestDockingEngineFactory(unittest.TestCase):
    def setUp(self):
        self.receptor_path = Path("receptor.pdbqt")
        self.ligand_path = Path("ligand.pdbqt")
        self.output_dir = Path("output")

        self.path_patcher = patch("pathlib.Path.exists")
        self.mkdir_patcher = patch("pathlib.Path.mkdir")
        self.mock_exists = self.path_patcher.start()
        self.mock_mkdir = self.mkdir_patcher.start()
        self.mock_exists.return_value = True

    def tearDown(self):
        self.path_patcher.stop()
        self.mkdir_patcher.stop()

    def test_create_vina_engine(self):
        engine = DockingEngineFactory.create_engine("vina", self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, VinaEngine)

    def test_create_unknown_engine(self):
        with self.assertRaises(ValueError):
            DockingEngineFactory.create_engine("unknown", self.receptor_path, self.ligand_path, self.output_dir)


if __name__ == "__main__":
    unittest.main()
