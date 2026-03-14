# bio-analyze-docking

基于 Vina 的自动化分子对接模块，提供从受体/配体准备到对接模拟及结果汇总的全流程解决方案。支持单次对接与高通量批量对接。

## ✨ 核心特性 (Features)

- **批量处理 (Batch Processing)**：支持指定目录进行多对多（M个受体 x N个配体）的批量对接，自动处理任务调度。
- **断点续传 (Resumable)**：批量任务支持断点续传，意外中断后再次运行可跳过已完成的任务。
- **广泛格式支持**：
  - **受体**：支持 `.pdb`, `.cif`, `.mmcif` (自动转换为 PDB)。
  - **配体**：支持 `.sdf`, `.mol2`, `.pdb`, `.smi` (SMILES)。
- **结果汇总**：自动生成 `docking_summary.csv`，包含结合能、RMSD 及盒子参数。
- **复合物生成**：可选生成对接后的受体-配体复合物结构（PDB格式），便于 PyMOL 查看。
- **自动化准备**：集成 `Meeko` 和 `PDBFixer`，自动处理受体质子化、补全缺失原子及配体 PDBQT 转换。

## 🔧 依赖工具 (Dependencies)

- **AutoDock Vina** (via Python `vina` package)
- **Smina** (Advanced fork of Vina, must be installed in PATH)
- **Gnina** (Deep learning-based docking, must be installed in PATH)
- **Meeko** (Ligand/Receptor preparation)
- **RDKit** (Chemical informatics)
- **OpenBabel** (Backup for receptor preparation)
- **Gemmi** (CIF/mmCIF support)
- **PDBFixer** (Receptor repair)

## 🚀 使用方法 (Usage)

### 1. 准备受体 (Receptor Preparation)

将 PDB/CIF 文件转换为 PDBQT 格式，自动添加极性氢。

```bash
# 单个文件
uv run bioanalyze docking prepare-receptor receptor.pdb -o receptor.pdbqt

# 支持 CIF 格式
uv run bioanalyze docking prepare-receptor structure.cif -o structure.pdbqt
```

### 2. 准备配体 (Ligand Preparation)

将 SDF/SMILES/PDB 文件转换为 PDBQT 格式，自动生成 3D 构象并处理柔性键。

```bash
uv run bioanalyze docking prepare-ligand ligand.sdf -o ligand.pdbqt
```

### 3. 运行对接 (Run Docking)

#### 场景 A：单次对接 (Single Docking)

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --center-x 10.5 --center-y 20.0 --center-z 30.0 \
    --size-x 20 --size-y 20 --size-z 20
```

#### 场景 B：批量对接 (Batch Docking)

只需将 `--receptor` 或 `--ligand` 指定为目录，程序将自动扫描目录下的所有支持文件并进行两两对接。

```bash
uv run bioanalyze docking run \
    --receptor ./receptors_dir \
    --ligand ./ligands_dir \
    --output ./batch_results \
    --padding 4.0  # 自动根据受体计算盒子，并在四周增加 4.0A 的填充
```

**批量对接输出结构：**

```
batch_results/
├── dock_results/
│   ├── poses/          # 对接姿态 (PDBQT)
│   │   └── receptor_name/
│   │       └── ligand_name_docked.pdbqt
│   └── complex/        # (可选) 复合物结构 (PDB)
├── docking_summary.csv # 汇总表格 (包含 Affinity, RMSD 等)
├── logs/               # 每个任务的独立日志
└── configs.json        # 运行配置记录
```

#### 场景 C：基于参考配体自动定义盒子 (Autobox)

使用共晶配体自动确定对接中心和范围。

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --autobox-ligand reference_ligand.sdf \
    --padding 4.0
```

#### 场景 D：使用配置文件

通过 `config.json` 或 `config.yaml` 管理复杂参数：

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

#### 场景 E：使用 Smina 或 Gnina 引擎

如果系统 PATH 中安装了 `smina` 或 `gnina`，可以通过 `--engine` 参数启用：

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --engine gnina
```

## 📦 Python API

### 1. 单次对接 (`run_docking`)

```python
from bio_analyze_docking import run_docking
from pathlib import Path

result = run_docking(
    receptor=Path("receptor.pdb"),       # 支持 PDB/PDBQT/CIF
    ligand=Path("ligand.sdf"),           # 支持 SDF/MOL2/PDB/SMILES
    output_dir=Path("./results"),
    center=[10.5, 20.0, 30.0],           # 盒子中心 [x, y, z]
    size=[20.0, 20.0, 20.0],             # 盒子大小 [x, y, z]
    exhaustiveness=8,                    # 搜索穷尽性 (默认 8)
    n_poses=9,                           # 输出姿态数量
    output_docked_lig_recep_struct=True, # 是否保存复合物 PDB (需要 PyMOL)
    charge_model="gasteiger"             # 电荷模型
)

print(f"Best Score: {result['best_score']}")
```

### 2. 批量对接 (`run_docking_batch`)

```python
from bio_analyze_docking import run_docking_batch
from pathlib import Path

results = run_docking_batch(
    receptors=Path("./receptors_dir"),  # 受体目录
    ligands=Path("./ligands_dir"),      # 配体目录
    output_dir=Path("./batch_results"),
    padding=4.0,                        # 自动盒子填充
    exhaustiveness=8
)

# results 是包含每个对接任务结果的列表
```

### 3. 底层组件 (Components)

您也可以单独使用底层的准备和引擎类：

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
print(f"Best affinity: {engine.score()}")
```
