import os
import shutil
import subprocess
from pathlib import Path

import pytest
from bio_analyze_docking.engines.base import BaseDockingEngine
from bio_analyze_docking.engines.vina import VinaEngine

MOCK_RESULTS_DIR = Path(__file__).parent / "data" / "mock_results"


@pytest.fixture(autouse=True)
def mock_docking_engines(request, monkeypatch):
    """
    Mock external command lines and engines to avoid slow docking in tests.
    """
    # 1. Mock shutil.which so gnina and smina are always "found"
    original_which = shutil.which

    def mock_which(cmd, mode=os.F_OK | os.X_OK, path=None):
        if cmd in ["gnina", "smina", "gnina.exe", "smina.exe"]:
            return f"/mock/path/to/{cmd}"
        return original_which(cmd, mode, path)

    monkeypatch.setattr(shutil, "which", mock_which)

    # 2. Mock subprocess.run for gnina and smina
    original_run = subprocess.run

    def mock_run(args, **kwargs):
        cmd = args[0] if isinstance(args, list) else args
        cmd_str = str(cmd)

        if "gnina" in cmd_str:
            if "--help" in args:
                return subprocess.CompletedProcess(args, 0, stdout="gnina receptor cnn", stderr="")
            # Extract --out param
            try:
                out_idx = args.index("--out")
                out_path = Path(args[out_idx + 1])
                shutil.copy2(MOCK_RESULTS_DIR / "gnina_out.pdbqt", out_path)
            except ValueError:
                pass
            return subprocess.CompletedProcess(args, 0, stdout="Mock Gnina Output", stderr="")

        elif "smina" in cmd_str:
            if "--help" in args:
                return subprocess.CompletedProcess(args, 0, stdout="smina receptor ligand", stderr="")
            try:
                out_idx = args.index("--out")
                out_path = Path(args[out_idx + 1])
                shutil.copy2(MOCK_RESULTS_DIR / "smina_out.pdbqt", out_path)
            except ValueError:
                pass
            return subprocess.CompletedProcess(args, 0, stdout="Mock Smina Output", stderr="")

        return original_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    # 3. Mock VinaEngine
    original_vina_init = VinaEngine.__init__

    def mock_vina_init(self, receptor, ligand, output_dir):
        # Call BaseDockingEngine.__init__ to setup paths
        BaseDockingEngine.__init__(self, receptor, ligand, output_dir)
        # Fake engine
        self.engine = type(
            "MockVina",
            (),
            {
                "compute_vina_maps": lambda *args, **kwargs: None,
                "energies": lambda self, n_poses=1: [[-3.565, 0.0, 0.0]] * min(n_poses, 1),
                "write_poses": lambda self, path, n_poses=1, overwrite=True: Path(path).touch(),
            },
        )()

    def mock_vina_dock(self, exhaustiveness=8, n_poses=9, min_rmsd=1.0, timeout=3600):
        pass  # Do nothing

    def mock_vina_save_results(self, output_name="docked.pdbqt", output_dir=None):
        target_dir = output_dir if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / output_name
        shutil.copy2(MOCK_RESULTS_DIR / "vina_out.pdbqt", out_path)
        return out_path

    def mock_vina_score(self):
        return -3.565

    def mock_vina_get_all_poses_info(self, n_poses=9):
        return [{"pose": 1, "affinity": -3.565, "rmsd_lb": 0.0, "rmsd_ub": 0.0}]

    monkeypatch.setattr(VinaEngine, "__init__", mock_vina_init)
    monkeypatch.setattr(VinaEngine, "compute_box", lambda self, center, size: None)
    monkeypatch.setattr(VinaEngine, "dock", mock_vina_dock)
    monkeypatch.setattr(VinaEngine, "save_results", mock_vina_save_results)
    monkeypatch.setattr(VinaEngine, "score", mock_vina_score)
    monkeypatch.setattr(VinaEngine, "get_all_poses_info", mock_vina_get_all_poses_info)

    # 4. Mock PyMOL merge complex to speed up tests
    import bio_analyze_docking.engines.gnina
    import bio_analyze_docking.engines.smina
    import bio_analyze_docking.engines.vina
    import bio_analyze_docking.utils

    class MockCmd:
        def reinitialize(self):
            pass

    bio_analyze_docking.engines.vina.cmd = MockCmd()
    bio_analyze_docking.engines.smina.cmd = MockCmd()
    bio_analyze_docking.engines.gnina.cmd = MockCmd()

    def mock_merge_complex(receptor_pdbqt, docked_ligands_pdbqt, output_dir, n_poses=1, output_name_prefix="complex"):
        for i in range(1, n_poses + 1):
            (Path(output_dir) / f"{output_name_prefix}_{i}.pdb").touch()

    monkeypatch.setattr(bio_analyze_docking.engines.vina, "merge_complex_with_pymol", mock_merge_complex)
    monkeypatch.setattr(bio_analyze_docking.engines.smina, "merge_complex_with_pymol", mock_merge_complex)
    monkeypatch.setattr(bio_analyze_docking.engines.gnina, "merge_complex_with_pymol", mock_merge_complex)

    # 5. Mock prep module if not running test_prep.py
    if "test_prep.py" not in request.node.nodeid:
        import concurrent.futures

        import bio_analyze_docking.nodes
        import bio_analyze_docking.prep

        # Patch ProcessPoolExecutor to ThreadPoolExecutor so monkeypatch works
        monkeypatch.setattr(bio_analyze_docking.nodes, "ProcessPoolExecutor", concurrent.futures.ThreadPoolExecutor)

        def mock_prepare_receptor(input_file, output_file, **kwargs):
            pre_computed = MOCK_RESULTS_DIR / "prepared_receptors" / f"{Path(input_file).stem}.pdbqt"
            if pre_computed.exists():
                shutil.copy2(pre_computed, output_file)
            else:
                Path(output_file).touch()
            return Path(output_file)

        def mock_prepare_ligand(input_file, output_file, **kwargs):
            pre_computed = MOCK_RESULTS_DIR / "prepared_ligands" / f"{Path(input_file).stem}.pdbqt"
            if pre_computed.exists():
                shutil.copy2(pre_computed, output_file)
            else:
                Path(output_file).touch()
            return Path(output_file)

        monkeypatch.setattr(bio_analyze_docking.prep, "prepare_receptor", mock_prepare_receptor)
        monkeypatch.setattr(bio_analyze_docking.prep, "prepare_ligand", mock_prepare_ligand)
