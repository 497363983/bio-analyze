from __future__ import annotations

from pathlib import Path


def example_dock(receptor_pdb: Path, ligand_sdf: Path) -> dict[str, str]:
    return {"receptor": str(receptor_pdb), "ligand": str(ligand_sdf), "status": "stub"}

