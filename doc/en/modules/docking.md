# bio-analyze-docking

Automated molecular docking module based on Vina, providing a full-process solution from receptor/ligand preparation to docking simulation and result summary. Supports single docking and high-throughput batch docking.

## ✨ Core Features

- **Batch Processing**: Supports batch docking of multiple receptors x multiple ligands in specified directories, automatically handling task scheduling.
- **Resumable**: Batch tasks support breakpoint resumption; re-running after an interruption skips completed tasks.
- **Wide Format Support**:
  - **Receptor**: Supports `.pdb`, `.cif`, `.mmcif` (automatically converted to PDB).
  - **Ligand**: Supports `.sdf`, `.mol2`, `.pdb`, `.smi` (SMILES).
- **Result Summary**: Automatically generates `docking_summary.csv`, including binding affinity, RMSD, and box parameters.
- **Complex Generation**: Optionally generates docked receptor-ligand complex structures (PDB format) for easy viewing in PyMOL.
- **Automated Preparation**: Integrates `Meeko` and `PDBFixer` to automatically handle receptor protonation, missing atoms, and ligand PDBQT conversion.

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

### 1. Prepare Receptor

Convert PDB/CIF files to PDBQT format, automatically adding polar hydrogens.

```bash
# Single file
uv run bioanalyze docking prepare-receptor receptor.pdb -o receptor.pdbqt

# Support CIF format
uv run bioanalyze docking prepare-receptor structure.cif -o structure.pdbqt
```

### 2. Prepare Ligand

Convert SDF/SMILES/PDB files to PDBQT format, automatically generating 3D conformations and handling flexible bonds.

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

Simply specify `--receptor` or `--ligand` as directories, and the program will automatically scan all supported files and perform pairwise docking.

```bash
uv run bioanalyze docking run \
    --receptor ./receptors_dir \
    --ligand ./ligands_dir \
    --output ./batch_results \
    --padding 4.0  # Automatically calculate box based on receptor and add 4.0A padding
```

**Batch Docking Output Structure:**

```
batch_results/
├── dock_results/
│   ├── poses/          # Docking poses (PDBQT)
│   │   └── receptor_name/
│   │       └── ligand_name_docked.pdbqt
│   └── complex/        # (Optional) Complex structure (PDB)
├── docking_summary.csv # Summary table (Affinity, RMSD, etc.)
├── logs/               # Independent logs for each task
└── configs.json        # Run configuration record
```

#### Scenario C: Autobox with Reference Ligand

Use a co-crystallized ligand to automatically define the docking center and size.

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --autobox-ligand reference_ligand.sdf \
    --padding 4.0
```

#### Scenario D: Using Configuration File

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

If `smina` or `gnina` is installed in system PATH, enable via `--engine`:

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
    n_poses=9,                           # Number of output poses
    output_docked_lig_recep_struct=True, # Save complex PDB (requires PyMOL)
    charge_model="gasteiger"             # Charge model
)

print(f"Best Score: {result['best_score']}")
```

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
```

### 3. Components

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
