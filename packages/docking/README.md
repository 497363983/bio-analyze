# bio-analyze-docking

基于 Vina 的自动化分子对接模块，提供从受体/配体准备到对接模拟的全流程解决方案。

## 🔧 依赖工具 (Dependencies)

- **AutoDock Vina** (via Python `vina` package)
- **Meeko** (Ligand preparation)
- **RDKit** (Chemical informatics)
- **OpenBabel** (Receptor preparation, external CLI required)

## 🚀 使用方法 (Usage)

### 1. 准备受体 (Receptor Preparation)

将 PDB 文件转换为 PDBQT 格式，自动添加极性氢。

```bash
uv run bioanalyze docking prepare-receptor receptor.pdb -o receptor.pdbqt
```

### 2. 准备配体 (Ligand Preparation)

将 SDF/SMILES/PDB 文件转换为 PDBQT 格式，自动生成 3D 构象并处理柔性键。

```bash
uv run bioanalyze docking prepare-ligand ligand.sdf -o ligand.pdbqt
```

### 3. 运行对接 (Run Docking)

#### 方式 A：指定对接盒子 (Manual Box)

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --center-x 10.5 --center-y 20.0 --center-z 30.0 \
    --size-x 20 --size-y 20 --size-z 20
```

#### 方式 B：基于参考配体自动定义盒子 (Autobox)

使用共晶配体自动确定对接中心和范围。

```bash
uv run bioanalyze docking run \
    --receptor receptor.pdbqt \
    --ligand ligand.pdbqt \
    --output ./results \
    --autobox-ligand reference_ligand.sdf \
    --padding 4.0
```

#### 方式 C：使用配置文件 (JSON/YAML)

通过配置文件批量管理参数。支持 `.json`、`.yaml` 或 `.yml` 格式。

**config.json 示例:**

```json
{
  "receptor": "receptor.pdbqt",
  "ligand": "ligand.pdbqt",
  "output_dir": "./results",
  "autobox_ligand": "reference_ligand.sdf",
  "padding": 4.0,
  "exhaustiveness": 8,
  "n_poses": 9,
  "engine": "vina"
}
```

**运行命令:**

```bash
uv run bioanalyze docking run --config config.json
```

*注意：命令行参数优先级高于配置文件。例如 `uv run bioanalyze docking run --config config.json --exhaustiveness 32` 将覆盖文件中的 exhaustiveness 设置。*

## 📦 Python API

```python
from bio_analyze_docking import run_docking

result = run_docking(
    receptor="receptor.pdb",
    ligand="ligand.sdf",
    output_dir="./results",
    autobox_ligand="ref_ligand.sdf",
    engine="vina"  # 可选: "vina", "gnina" (需安装)
)
print(f"Best Score: {result['best_score']}")
```
