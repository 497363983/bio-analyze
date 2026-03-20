---
---

# bio-analyze-docking

基于 Vina 的自动化分子对接模块，提供从受体/配体准备到对接模拟、结果汇总的全流程解决方案。支持单次对接和高通量批量对接。

## ✨ 核心特性 (Features)

- **批量处理**：支持基于目录的多对多（M 个受体 x N 个配体）批量对接，自动处理任务调度。
- **断点续传**：批量任务支持断点续传，意外中断后可跳过已完成的任务。
- **多格式支持**：
  - **受体**：支持 `.pdb`, `.cif`, `.mmcif` (自动转换为 PDB)。
  - **配体**：支持 `.sdf`, `.mol2`, `.pdb`, `.smi` (SMILES)。
- **结果汇总**：自动生成 `docking_summary.csv`，包含结合能、RMSD、盒子参数等信息。
- **复合物生成**：可选生成对接后的受体-配体复合物结构（PDB 格式），方便 PyMOL 查看。
- **自动化准备**：集成 `Meeko` 和 `PDBFixer`，自动处理受体加氢、缺失原子补全、配体 PDBQT 转换。

## 🔧 依赖 (Dependencies)

- **AutoDock Vina** (通过 Python `vina` 包)
- **Smina** (Vina 的高级分支，需安装在 PATH 中)
- **Gnina** (基于深度学习的对接，需安装在 PATH 中)
- **Meeko** (配体/受体准备)
- **RDKit** (化学信息学)
- **OpenBabel** (备用受体准备)
- **Gemmi** (CIF/mmCIF 支持)
- **PDBFixer** (受体修复)

## 🚀 快速开始 (Usage)

### 1. 准备受体 (Receptor Preparation)

将 PDB/CIF 文件转换为 PDBQT 格式，自动添加极性氢。

<ParamTable params-path="docking/prepare-receptor_cli" />

```bash
# 单文件
uv run bioanalyze docking prepare-receptor receptor.pdb -o receptor.pdbqt

# 支持 CIF 格式
uv run bioanalyze docking prepare-receptor structure.cif -o structure.pdbqt
```

### 2. 准备配体 (Ligand Preparation)

将 SDF/SMILES/PDB 文件转换为 PDBQT 格式，自动生成 3D 构象并处理可旋转键。

<ParamTable params-path="docking/prepare-ligand_cli" />

```bash
uv run bioanalyze docking prepare-ligand ligand.sdf -o ligand.pdbqt
```

### 3. 运行对接 (Run Docking)

`run` 命令已重构为引擎特定的子命令（`vina`, `smina`, `gnina`, `haddock`），以便为每个引擎提供准确的参数选项。

#### Vina 引擎 (`run vina`)
默认的 AutoDock Vina 引擎。
<ParamTable params-path="docking/run_vina_cli" />

```bash
# 单次对接
uv run bioanalyze docking run vina \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --center-x 10.5 --center-y 20.0 --center-z 30.0 \
    --size-x 20 --size-y 20 --size-z 20

# 批量对接
uv run bioanalyze docking run vina \
    --receptor ./receptors_dir \
    --ligand ./ligands_dir \
    --output ./batch_results \
    --padding 4.0
```

#### Smina 引擎 (`run smina`)
<ParamTable params-path="docking/run_smina_cli" />

```bash
uv run bioanalyze docking run smina --receptor rec.pdbqt --ligand lig.pdbqt -o ./results
```

#### Gnina 引擎 (`run gnina`)
<ParamTable params-path="docking/run_gnina_cli" />

```bash
uv run bioanalyze docking run gnina --receptor rec.pdbqt --ligand lig.pdbqt -o ./results
```

#### HADDOCK 引擎 (`run haddock`)
数据驱动的柔性对接。注意 HADDOCK 不需要提供盒子参数（`center`, `size`）。
<ParamTable params-path="docking/run_haddock_cli" />

```bash
uv run bioanalyze docking run haddock --receptor rec.pdb --ligand lig.pdb -o ./results --n-poses 10

# 使用自定义 HADDOCK3 配置文件
uv run bioanalyze docking run haddock --receptor rec.pdb --ligand lig.pdb -o ./results --haddock-config custom.cfg
```

#### 使用配置文件
您可以通过 `config.json` 或 `config.yaml` 为任何子命令管理复杂参数：
```bash
uv run bioanalyze docking run vina --config config.json
```

## 📦 Python API

### 1. 特定引擎的单次对接

API 为每个引擎提供了特定的函数，以确保类型安全和参数的准确性。

```python
from bio_analyze_docking import run_vina, run_haddock
from pathlib import Path

# Vina 示例
vina_res = run_vina(
    receptor=Path("receptor.pdb"),
    ligand=Path("ligand.sdf"),
    output_dir=Path("./results_vina"),
    center=[10.5, 20.0, 30.0],
    size=[20.0, 20.0, 20.0],
    exhaustiveness=8
)

# HADDOCK 示例 (无需盒子参数)
haddock_res = run_haddock(
    receptor=Path("protein.pdb"),
    ligand=Path("ligand.pdb"),
    output_dir=Path("./results_haddock"),
    n_poses=10
)
```

**参数 (Vina):**
<ParamTable params-path="docking/run_vina_api" />

**参数 (Haddock):**
<ParamTable params-path="docking/run_haddock_api" />

### 2. 特定引擎的批量对接

类似地，为每个引擎提供了特定的批量处理函数（如 `run_vina_batch`, `run_haddock_batch` 等）。

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

**参数 (Vina Batch):**
<ParamTable params-path="docking/run_vina_batch_api" />

### 3. 底层组件 (Components)

您也可以单独使用底层的准备类和引擎类：

```python
from bio_analyze_docking import prepare_receptor, prepare_ligand, DockingEngine

# 准备文件
rec_pdbqt = prepare_receptor("protein.pdb", "protein.pdbqt")
lig_pdbqt = prepare_ligand("ligand.sdf", "ligand.pdbqt")

# 初始化引擎
engine = DockingEngine(rec_pdbqt, lig_pdbqt, output_dir=Path("./out"))

# 计算盒子
engine.compute_box(center=[0, 0, 0], size=[20, 20, 20])

# 运行对接
engine.dock()

# 保存结果
engine.save_results("docked.pdbqt")
print(f"最佳亲和力: {engine.score()}")
```
