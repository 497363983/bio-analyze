# bio-analyze-docking

[![PyPI Version](https://img.shields.io/pypi/v/bio-analyze-docking?label=PyPI&include_prereleases&sort=semver&logo=python)](https://pypi.org/project/bio-analyze-docking/)
[![codecov](https://codecov.io/gh/497363983/bio-analyze/graph/badge.svg?token=I78TXQBORK&component=docking)](https://codecov.io/gh/497363983/bio-analyze)
![Python Version](https://img.shields.io/pypi/pyversions/bio-analyze-docking.svg)

An automated molecular docking module based on Vina, providing a full-pipeline solution from receptor/ligand preparation to docking simulation and result summarization. Supports both single docking and high-throughput batch docking.

## ✨ Features

- **Batch Processing**: Supports multi-to-multi (M receptors x N ligands) batch docking by specifying directories, automatically handling task scheduling.
- **Resumable**: Batch tasks support resuming; if interrupted, restarting will skip already completed tasks.
- **Wide Format Support**:
  - **Receptor**: Supports `.pdb`, `.cif`, `.mmcif` (automatically converted to PDB).
  - **Ligand**: Supports `.sdf`, `.mol2`, `.pdb`, `.smi` (SMILES).
- **Result Summarization**: Automatically generates `docking_summary.csv`, containing binding affinities, RMSD, and box parameters.
- **Complex Generation**: Optionally generates the docked receptor-ligand complex structure (PDB format) for easy viewing in PyMOL.
- **Automated Preparation**: Integrates `Meeko` and `PDBFixer` to automatically handle receptor protonation, missing atom completion, and ligand PDBQT conversion.

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

### 1. Receptor Preparation

Converts PDB/CIF files to PDBQT format, automatically adding polar hydrogens.

```bash
# Single file
uv run bioanalyze docking prepare-receptor receptor.pdb -o receptor.pdbqt

# CIF format support
uv run bioanalyze docking prepare-receptor structure.cif -o structure.pdbqt
```

### 2. Ligand Preparation

Converts SDF/SMILES/PDB files to PDBQT format, automatically generating 3D conformations and handling flexible bonds.

```bash
uv run bioanalyze docking prepare-ligand ligand.sdf -o ligand.pdbqt
```

### 3. Run Docking

#### Scenario A: Single Docking

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --center-x 10.5 --center-y 20.0 --center-z 30.0 \
    --size-x 20 --size-y 20 --size-z 20
```

#### Scenario B: Batch Docking

Simply specify `--receptor` or `--ligand` as directories, and the program will automatically scan for all supported files and perform pairwise docking.

```bash
uv run bioanalyze docking run \
    --receptor ./receptors_dir \
    --ligand ./ligands_dir \
    --output ./batch_results \
    --padding 4.0  # Automatically calculate the box based on the receptor and add 4.0A padding
```

**Batch Docking Output Structure:**

```
batch_results/
├── dock_results/
│   ├── poses/          # Docked poses (PDBQT)
│   │   └── receptor_name/
│   │       └── ligand_name_docked.pdbqt
│   └── complex/        # (Optional) Complex structures (PDB)
├── docking_summary.csv # Summary table (contains Affinity, RMSD, etc.)
├── logs/               # Independent logs for each task
└── configs.json        # Run configuration record
```

#### Scenario C: Autoboxing based on Reference Ligand

Use a co-crystallized ligand to automatically determine the docking center and extent.

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --autobox-ligand reference_ligand.sdf \
    --padding 4.0
```

#### Scenario D: Using a Configuration File

Manage complex parameters via `config.json` or `config.yaml`:

```json
{
  "receptor": "./receptors_dir",
  "ligand": "./ligands_dir",
  "output_dir": "./results",
  "exhaustiveness": 8,
  "n_poses": 9,
  "engine": "vina" // or "smina", "gnina"
}
```

```bash
uv run bioanalyze docking run --config config.json
```

#### Scenario E: Using Smina or Gnina Engine

If `smina` or `gnina` is installed in the system PATH, you can enable them via the `--engine` parameter:

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --engine gnina
```

## 📦 Python API

### 1. Single Docking (`run_docking`)

```python
from bio_analyze_docking import run_docking
from pathlib import Path

result = run_docking(
    receptor=Path("receptor.pdb"),       # Supports PDB/PDBQT/CIF
    ligand=Path("ligand.sdf"),           # Supports SDF/MOL2/PDB/SMILES
    output_dir=Path("./results"),
    center=[10.5, 20.0, 30.0],           # Box center [x, y, z]
    size=[20.0, 20.0, 20.0],             # Box size [x, y, z]
    exhaustiveness=8,                    # Search exhaustiveness (default 8)
    n_poses=9,                           # Number of poses to output
    output_docked_lig_recep_struct=True, # Whether to save complex PDB (requires PyMOL)
    charge_model="gasteiger"             # Charge model
)

print(f"Best Score: {result['best_score']}")
```

**Parameters:**

- `receptor`: Receptor file path (PDB/PDBQT/CIF/MMCIF).
- `ligand`: Ligand file path (SDF/MOL2/PDB/SMILES).
- `output_dir`: Output directory.
- `center`: Box center `[x, y, z]`.
- `size`: Box size `[x, y, z]` (default `[20, 20, 20]`).
- `autobox_ligand`: (Optional) Reference ligand path for automatic box definition (overrides `center` and `size`).
- `padding`: (Optional) Automatic box padding (Angstroms).
- `exhaustiveness`: Vina search exhaustiveness (default 8).
- `n_poses`: Number of poses to generate (default 9).
- `output_docked_lig_recep_struct`: Whether to generate complex PDB files (default False).
- `charge_model`: Charge model used during receptor preparation (default 'gasteiger').

### 2. Batch Docking (`run_docking_batch`)

```python
from bio_analyze_docking import run_docking_batch
from pathlib import Path

results = run_docking_batch(
    receptors=Path("./receptors_dir"),  # Receptor directory
    ligands=Path("./ligands_dir"),      # Ligand directory
    output_dir=Path("./batch_results"),
    padding=4.0,                        # Auto box padding
    exhaustiveness=8
)

# results is a list containing the results of each docking task
```

**Parameters:**

- `receptors`: Receptor directory path or list of files.
- `ligands`: Ligand directory path or list of files.
- `output_dir`: Base output directory.
- `summary_filename`: Summary file name (default "docking_summary.csv").
- Other parameters are the same as `run_docking`.

### 3. Underlying Components

You can also use the underlying preparation and engine classes independently:

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
