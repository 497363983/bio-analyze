---
order: 2
---
# 安装指南

`bio-analyze` 是一个功能强大的生物信息学分析工具箱，支持通过 Conda、Pip 或 Docker 进行安装。

## 方法 1: 使用 Conda 安装 (推荐)

Conda 是首选的安装方式，因为它可以自动处理复杂的生物信息学软件依赖（如 `samtools`、`star` 等）。

### 1. 安装 Conda/Mamba

首先，确保您已安装 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 [Mambaforge](https://github.com/conda-forge/miniforge)（推荐，速度更快）。

### 2. 创建环境并安装

```bash
# 创建名为 bio-analyze 的新环境
conda create -n bio-analyze -c bioconda -c conda-forge bio-analyze

# 激活环境
conda activate bio-analyze
```

### 3. 验证安装

```bash
bio-analyze --version
```

## 方法 2: 使用 Pip 安装

如果您只需要使用 Python 分析模块（如绘图、统计分析），且已经自行配置好了生物信息学工具环境，可以通过 pip 安装。

```bash
pip install bio-analyze
```

> **注意**: 此方法**不会**安装 `star`、`salmon` 等外部二进制依赖。您需要手动确保这些工具在系统 PATH 中。

## 方法 3: 使用 Docker 镜像

如果您不想配置本地环境，可以直接使用我们预构建的 Docker 镜像，其中包含了所有必要的工具。

### 拉取镜像

```bash
docker pull bioanalyze/bio-analyze:latest
```

### 运行分析

将本地数据目录挂载到容器中（例如将当前目录 `$(pwd)` 挂载到 `/data`）：

```bash
docker run --rm -v $(pwd):/data bioanalyze/bio-analyze:latest \
    bio-analyze plot volcano /data/results.csv
```

## 常见问题

### 依赖冲突

如果遇到依赖冲突，尝试创建一个干净的环境，或者使用 `mamba` 代替 `conda` 以获得更快更好的依赖解析：

```bash
mamba create -n bio-analyze -c bioconda -c conda-forge bio-analyze
```
