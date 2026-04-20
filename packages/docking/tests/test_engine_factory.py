"""Tests for the docking compatibility factory backed by the shared engine registry."""

from __future__ import annotations

from pathlib import Path

from bio_analyze_core.engine import EngineRegistry
from bio_analyze_docking.engines.base import BaseDockingEngine
from bio_analyze_docking.engines.factory import DockingEngineFactory
from bio_analyze_docking.engines.vina import VinaEngine


class DummyDockingEngine(BaseDockingEngine):
    """Minimal runtime-registered docking engine used for factory tests."""
    ENGINE_NAME = "dummy"

    def __init__(self, *args, **kwargs):
        self.center = None
        self.size = None
        super().__init__(*args, **kwargs)

    def compute_box(self, center: list[float], size: list[float]):
        self.center = center
        self.size = size

    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0, timeout: float = 3600):
        return None

    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Path | None = None) -> Path:
        target_dir = output_dir or self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        out_file = target_dir / output_name
        out_file.write_text("pose", encoding="utf-8")
        return out_file

    def save_complexes(
        self,
        n_complexes: int | None = None,
        output_dir: Path | None = None,
        output_name_prefix: str = "complex_pose",
    ):
        return None

    def score(self) -> float:
        return -1.0

    def get_all_poses_info(self, n_poses: int = 9) -> list[dict]:
        return []


def test_factory_returns_registered_default_engine():
    """The compatibility factory should expose built-in engines."""
    engine_class = DockingEngineFactory.get_engine_class("vina")

    assert engine_class is VinaEngine


def test_factory_can_register_runtime_engine(tmp_path):
    """Runtime-registered engines should be creatable through the factory."""
    receptor = tmp_path / "receptor.pdbqt"
    ligand = tmp_path / "ligand.pdbqt"
    receptor.write_text("receptor", encoding="utf-8")
    ligand.write_text("ligand", encoding="utf-8")

    DockingEngineFactory.register_engine("dummy", DummyDockingEngine)
    engine = DockingEngineFactory.create_engine("dummy", receptor, ligand, tmp_path / "out")

    assert isinstance(engine, DummyDockingEngine)
    assert EngineRegistry.get("docking", "dummy") is DummyDockingEngine
