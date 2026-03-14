# 安装指南

## 一键安装脚本 (Linux/macOS/WSL)

如果您不熟悉 Docker，或者希望在本地环境中直接运行工具箱，我们提供了一个自动化安装脚本。该脚本会自动创建 Conda 环境并安装所有必要的依赖。

### 前置条件

- **操作系统**: Linux (推荐 Ubuntu), macOS, 或 Windows WSL (Windows Subsystem for Linux)。
- **Conda**: 必须已安装 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 [Mambaforge](https://github.com/conda-forge/miniforge)。

### 运行安装脚本

在项目根目录下运行：

```bash
bash setup.sh
```

脚本将自动执行以下步骤：

1. 检查 Conda/Mamba 环境。
2. 配置 Bioconda 等软件源。
3. 创建名为 `bio_analyse_env` 的虚拟环境。
4. 安装 `fastp`, `salmon`, `star`, `samtools` 等生物信息学工具。
5. 安装 `bio-analyse` 工具箱的所有模块。
6. 安装并配置 `pre-commit` 和 `commitizen`。

### 激活环境

安装完成后，根据提示激活环境即可使用：

```bash
conda activate bio_analyse_env
bioanalyze --help
```

## 使用 Docker (推荐)

为了简化环境配置，特别是复杂的生物信息学工具依赖，我们提供了 Docker 支持。

### 构建镜像

```bash
docker build -t bio-analyze:latest .
```

### 运行容器

```bash
# 挂载数据目录并运行
docker run -it --rm -v $(pwd)/data:/data bio-analyze:latest --help
```

或者使用 `docker-compose`:

```bash
docker-compose run --rm bio-analyze --help
```

### 进入交互式 Shell

```bash
docker run -it --rm --entrypoint bash -v $(pwd)/data:/data bio-analyze:latest
```
