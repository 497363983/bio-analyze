---
---

# bio-analyze-docking

Automated molecular docking module based on Vina, providing a full-process solution from receptor/ligand preparation to docking simulation and result summarization. Supports single docking and high-throughput batch docking.

## ✨ Core Features (Features)

- **Batch Processing**: Supports directory-based many-to-many (M receptors x N ligands) batch docking, automatically handling task scheduling.
- **Resumable**: Batch tasks support resumable execution, skipping completed tasks after accidental interruption.
- **Extensive Format Support**:
  - **Receptor**: Supports `.pdb`, `.cif`, `.mmcif` (automatically converted to PDB).
  - **Ligand**: Supports `.sdf`, `.mol2`, `.pdb`, `.smi` (SMILES).
- **Result Summary**: Automatically generates `docking_summary.csv`, containing binding affinity, RMSD, and box parameters.
- **Complex Generation**: Optionally generates docked receptor-ligand complex structures (PDB format) for easy viewing in PyMOL.
- **Automated Preparation**: Integrates `Meeko` and `PDBFixer`, automatically handling receptor protonation, missing atom completion, and ligand PDBQT conversion.

## 🔧 Dependencies

- **AutoDock Vina** (via Python `vina` package)
- **Smina** (Advanced fork of Vina, must be installed in PATH)
- **Gnina** (Deep learning-based docking, must be installed in PATH)
- **Meeko** (Ligand/Receptor preparation)
- **RDKit** (Chemical informatics)
- **OpenBabel** (Backup for receptor preparation)
- **Gemmi** (CIF/mmCIF support)
- **PDBFixer** (Receptor repair)

## 🚀 Usage

### 1. Prepare Receptor (Receptor Preparation)

Convert PDB/CIF files to PDBQT format, automatically adding polar hydrogens.

<ParamTable params-path="docking/prepare-receptor_cli" />

```bash
# Single file
uv run bioanalyze docking prepare-receptor receptor.pdb -o receptor.pdbqt

# Support CIF format
uv run bioanalyze docking prepare-receptor structure.cif -o structure.pdbqt
```

### 2. Prepare Ligand (Ligand Preparation)

Convert SDF/SMILES/PDB files to PDBQT format, automatically generating 3D conformations and handling flexible bonds.

<ParamTable params-path="docking/prepare-ligand_cli" />

```bash
uv run bioanalyze docking prepare-ligand ligand.sdf -o ligand.pdbqt
```

### 3. Run Docking

The `run` command has been refactored into engine-specific subcommands (`vina`, `smina`, `gnina`, `haddock`) to provide more accurate parameters for each engine.

#### Vina Engine (`run vina`)
The default AutoDock Vina engine.
<ParamTable params-path="docking/run_vina_cli" />

```bash
# Single Docking
uv run bioanalyze docking run vina \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --center-x 10.5 --center-y 20.0 --center-z 30.0 \
    --size-x 20 --size-y 20 --size-z 20

# Batch Docking
uv run bioanalyze docking run vina \
    --receptor ./receptors_dir \
    --ligand ./ligands_dir \
    --output ./batch_results \
    --padding 4.0
```

#### Smina Engine (`run smina`)
<ParamTable params-path="docking/run_smina_cli" />

```bash
uv run bioanalyze docking run smina --receptor rec.pdbqt --ligand lig.pdbqt -o ./results
```

#### Gnina Engine (`run gnina`)
<ParamTable params-path="docking/run_gnina_cli" />

```bash
uv run bioanalyze docking run gnina --receptor rec.pdbqt --ligand lig.pdbqt -o ./results
```

#### HADDOCK Engine (`run haddock`)
Information-driven flexible docking. Note that HADDOCK does not require box parameters (`center`, `size`).
<ParamTable params-path="docking/run_haddock_cli" />

```bash
uv run bioanalyze docking run haddock --receptor rec.pdb --ligand lig.pdb -o ./results --n-poses 10

# Use custom HADDOCK3 configuration
uv run bioanalyze docking run haddock --receptor rec.pdb --ligand lig.pdb -o ./results --haddock-config custom.cfg
```

#### Using Configuration File
You can manage complex parameters via `config.json` or `config.yaml` for any subcommand:
```bash
uv run bioanalyze docking run vina --config config.json
```

## 📦 Python API

### 1. Engine-Specific Single Docking

The API provides specific functions for each engine to ensure type safety and correct parameters.

```python
from bio_analyze_docking import run_vina, run_haddock
from pathlib import Path

# Vina Example
vina_res = run_vina(
    receptor=Path("receptor.pdb"),
    ligand=Path("ligand.sdf"),
    output_dir=Path("./results_vina"),
    center=[10.5, 20.0, 30.0],
    size=[20.0, 20.0, 20.0],
    exhaustiveness=8
)

# HADDOCK Example (No box parameters required)
haddock_res = run_haddock(
    receptor=Path("protein.pdb"),
    ligand=Path("ligand.pdb"),
    output_dir=Path("./results_haddock"),
    n_poses=10
)
```

**Parameters (Vina):**
<ParamTable params-path="docking/run_vina_api" />

**Parameters (Haddock):**
<ParamTable params-path="docking/run_haddock_api" />

### 2. Batch Docking

Similarly, there are specific batch functions for each engine (`run_vina_batch`, `run_haddock_batch`, etc.).

```python
from bio_analyze_docking import run_vina_batch
from pathlib import Path

results = run_vina_batch(
    receptors=Path("./receptors_dir"),
    ligands=Path("./ligands_dir"),
    output_dir=Path("./batch_results"),
    padding=4.0
)
```

**Parameters (Vina Batch):**
<ParamTable params-path="docking/run_vina_batch_api" />

### 3. Underlying Components (Components)

You can also use the underlying preparation and engine classes separately:

```python
from bio_analyze_docking import prepare_receptor, prepare_ligand, DockingEngine

# Prepare files
rec_pdbqt = prepare_receptor("protein.pdb", "protein.pdbqt")
lig_pdbqt = prepare_ligand("ligand.sdf", "ligand.pdbqt")

# Initialize engine
engine = DockingEngine(rec_pdbqt, lig_pdbqt, output_dir=Path("./out"))

# Compute box
engine.compute_box(center=[0, 0, 0], size=[20, 20, 20])

# Run docking
engine.dock()

# Save results
engine.save_results("docked.pdbqt")
print(f"Best affinity: {engine.score()}")
```
