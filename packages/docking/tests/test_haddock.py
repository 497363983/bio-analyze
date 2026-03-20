import sys
from unittest.mock import MagicMock, patch

import pytest
from bio_analyze_docking.engines.haddock import HaddockEngine

# Mock haddock module so we don't need it installed to run tests
mock_haddock = MagicMock()
sys.modules["haddock"] = mock_haddock
sys.modules["haddock.clis"] = MagicMock()
sys.modules["haddock.clis.cli"] = MagicMock()


@pytest.fixture
def mock_haddock_env(tmp_path):
    rec = tmp_path / "receptor.pdb"
    rec.write_text("ATOM      1  N   ALA A   1      11.104  13.730  15.166  1.00 13.63           N")
    lig = tmp_path / "ligand.pdb"
    lig.write_text("ATOM      1  N   ALA A   1      11.104  13.730  15.166  1.00 13.63           N")
    out_dir = tmp_path / "output"
    out_dir.mkdir()

    return rec, lig, out_dir


def test_haddock_engine_init(mock_haddock_env):
    rec, lig, out_dir = mock_haddock_env
    engine = HaddockEngine(rec, lig, out_dir)
    assert engine.receptor == rec
    assert engine.ligand == lig
    assert engine.output_dir == out_dir
    assert HaddockEngine.get_receptor_ext() == ".pdb"
    assert HaddockEngine.get_ligand_ext() == ".pdb"


@patch("haddock.clis.cli.main")
def test_haddock_dock_custom_config(mock_run_haddock3, mock_haddock_env):
    rec, lig, out_dir = mock_haddock_env

    custom_cfg = out_dir / "custom.cfg"
    custom_cfg.write_text("[topoaa]\\n[rigidbody]\\nsampling=20", encoding="utf-8")

    engine = HaddockEngine(rec, lig, out_dir)
    engine._haddock_available = True

    engine.dock(n_poses=1, haddock_config=custom_cfg)

    assert mock_run_haddock3.call_count == 1

    # Check if config was generated using custom content
    generated_cfg = out_dir / "run.cfg"
    assert generated_cfg.exists()
    content = generated_cfg.read_text(encoding="utf-8")
    assert "sampling=20" in content
    assert str(rec.resolve()).replace("\\", "/") in content
    assert str(lig.resolve()).replace("\\", "/") in content
