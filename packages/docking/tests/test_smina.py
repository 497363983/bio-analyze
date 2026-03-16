import sys
import unittest
import subprocess
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
sys.modules["vina"] = MagicMock()
sys.modules["pymol"] = MagicMock()

from bio_analyze_docking.engines.factory import DockingEngineFactory
from bio_analyze_docking.engines.smina import SminaEngine


class TestSminaEngine(unittest.TestCase):
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

        # Mock shutil.which to pretend smina is installed
        self.which_patcher = patch("shutil.which")
        self.mock_which = self.which_patcher.start()
        self.mock_which.return_value = "/usr/bin/smina"

        # Mock subprocess.run
        self.subprocess_patcher = patch("subprocess.run")
        self.mock_subprocess = self.subprocess_patcher.start()
        self.mock_subprocess.return_value = MagicMock(stdout="Smina output", returncode=0)

    def tearDown(self):
        self.path_patcher.stop()
        self.mkdir_patcher.stop()
        self.which_patcher.stop()
        self.subprocess_patcher.stop()

    def test_initialization(self):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, SminaEngine)
        self.assertEqual(engine.smina_executable, "/usr/bin/smina")

    def test_initialization_fail(self):
        self.mock_which.return_value = None
        # Mock exists to return False for smina.exe check
        # We need to handle the call to exists()
        # The setup mocks it to always return True
        
        def side_effect(*args, **kwargs):
            return False

        self.mock_exists.side_effect = side_effect
        
        try:
            with self.assertRaises(RuntimeError):
                SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        finally:
            self.mock_exists.side_effect = None
            self.mock_exists.return_value = True

    def test_compute_box(self):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        self.assertEqual(engine.box_center, center)
        self.assertEqual(engine.box_size, size)

    def test_dock(self):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        
        engine.dock(exhaustiveness=16, n_poses=5, min_rmsd=2.0)
        
        self.mock_subprocess.assert_called_once()
        args, kwargs = self.mock_subprocess.call_args
        cmd_list = args[0]
        self.assertIn("/usr/bin/smina", cmd_list)
        self.assertIn("--receptor", cmd_list)
        self.assertIn(str(self.receptor_path), cmd_list)
        self.assertIn("--exhaustiveness", cmd_list)
        self.assertIn("16", cmd_list)

    def test_dock_fail(self):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        center = [10.0, 10.0, 10.0]
        size = [20.0, 20.0, 20.0]
        engine.compute_box(center, size)
        
        self.mock_subprocess.side_effect = subprocess.CalledProcessError(1, "smina", stderr="Error")
        with self.assertRaises(RuntimeError):
            engine.dock()

    @patch("shutil.copy2")
    def test_save_results(self, mock_copy):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        # Mock temp file existence
        # We need to control Path.exists more granularly
        # But we mocked it globally to return True
        
        engine.save_results("final.pdbqt")
        mock_copy.assert_called()

    def test_score(self):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        
        # Mock reading the output file
        mock_content = """
REMARK VINA RESULT:    -9.5      0.000      0.000
REMARK VINA RESULT:    -8.5      1.000      2.000
        """
        with patch("builtins.open", unittest.mock.mock_open(read_data=mock_content)):
            score = engine.score()
            self.assertEqual(score, -9.5)

    def test_get_all_poses_info(self):
        engine = SminaEngine(self.receptor_path, self.ligand_path, self.output_dir)
        
        mock_content = """
REMARK VINA RESULT:    -9.5      0.000      0.000
REMARK VINA RESULT:    -8.5      1.000      2.000
        """
        with patch("builtins.open", unittest.mock.mock_open(read_data=mock_content)):
            info = engine.get_all_poses_info(n_poses=2)
            self.assertEqual(len(info), 2)
            self.assertEqual(info[0]["affinity"], -9.5)
            self.assertEqual(info[1]["affinity"], -8.5)

    def test_factory_create_smina(self):
        engine = DockingEngineFactory.create_engine("smina", self.receptor_path, self.ligand_path, self.output_dir)
        self.assertIsInstance(engine, SminaEngine)

if __name__ == "__main__":
    unittest.main()
