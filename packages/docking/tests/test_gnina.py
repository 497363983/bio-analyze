import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock modules before importing
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
sys.modules["gemmi"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["openpyxl"] = MagicMock()
sys.modules["vina"] = MagicMock()
sys.modules["pymol"] = MagicMock()

from bio_analyze_docking.engines.factory import DockingEngineFactory
from bio_analyze_docking.engines.gnina import GninaEngine


class TestGninaEngine(unittest.TestCase):
    def setUp(self):
        self.receptor_path = Path("receptor.pdbqt")
        self.ligand_path = Path("ligand.pdbqt")
        self.output_dir = Path("output")

        # Mock Path operations
        self.path_patcher = patch("pathlib.Path.exists")
        self.mkdir_patcher = patch("pathlib.Path.mkdir")
        self.mock_exists = self.path_patcher.start()
        self.mock_mkdir = self.mkdir_patcher.start()
        self.mock_exists.return_value = True

        # Mock shutil.which to pretend gnina is installed
        self.which_patcher = patch("shutil.which")
        self.mock_which = self.which_patcher.start()
        self.mock_which.return_value = "/usr/bin/gnina"

        # Mock subprocess.run
        self.subprocess_patcher = patch("subprocess.run")
        self.mock_subprocess = self.subprocess_patcher.start()
        self.mock_subprocess.return_value = MagicMock(stdout="Gnina output", returncode=0)

    def tearDown(self):
        self.path_patcher.stop()
        self.mkdir_patcher.stop()
        self.which_patcher.stop()
        self.subprocess_patcher.stop()

    def test_initialization(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, GninaEngine)
        self.assertEqual(engine.gnina_executable, "/usr/bin/gnina")

    def test_compute_box(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        self.assertEqual(engine.box_center, center)
        self.assertEqual(engine.box_size, size)

    def test_dock(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        
        engine.dock(exhaustiveness=16, n_poses=5, min_rmsd=2.0)
        
        self.mock_subprocess.assert_called_once()
        args, kwargs = self.mock_subprocess.call_args
        cmd_list = args[0]
        self.assertIn("/usr/bin/gnina", cmd_list)
        self.assertIn("--receptor", cmd_list)
        self.assertIn(str(self.receptor_path), cmd_list)
        self.assertIn("--exhaustiveness", cmd_list)
        self.assertIn("16", cmd_list)

    def test_get_all_poses_info(self):
        engine = GninaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        
        mock_content = """
MODEL 1
REMARK VINA RESULT:    -9.5      0.000      0.000
REMARK CNNscore: 0.98
REMARK CNNaffinity: 9.0
ENDMDL
MODEL 2
REMARK VINA RESULT:    -8.5      1.000      2.000
REMARK CNNscore: 0.85
REMARK CNNaffinity: 8.0
ENDMDL
        """
        with patch("builtins.open", unittest.mock.mock_open(read_data=mock_content)):
            info = engine.get_all_poses_info(n_poses=2)
            self.assertEqual(len(info), 2)
            self.assertEqual(info[0]["affinity"], -9.5)
            self.assertEqual(info[0]["cnn_score"], 0.98)
            self.assertEqual(info[0]["cnn_affinity"], 9.0)
            self.assertEqual(info[1]["affinity"], -8.5)
            self.assertEqual(info[1]["cnn_score"], 0.85)

    def test_factory_create_gnina(self):
        engine = DockingEngineFactory.create_engine("gnina", self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, GninaEngine)

if __name__ == "__main__":
    unittest.main()
