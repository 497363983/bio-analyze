# bio-analyze

一个面向常用生物信息学分析任务的工具箱，采用 monorepo 组织多个独立模块，最终可通过统一 CLI 与 Python API 调用。

## Monorepo 结构

- `packages/core`：公共能力（配置、日志、IO、运行外部命令、资源管理等）
- `packages/cli`：统一命令行入口，支持插件式加载各模块子命令
- `packages/*`：各分析工具模块（例如 rna-seq、docking），每个模块是独立可发布包

## 📦 已有模块列表 (Modules)

目前工具箱包含以下核心模块，每个模块均可独立使用或通过 CLI 调用：

| 模块名称                 | 路径                 | 功能简介                                                                                         | 核心特点                                         |
| :----------------------- | :------------------- | :----------------------------------------------------------------------------------------------- | :----------------------------------------------- |
| 🧬**RNA-Seq 分析** | `packages/rna_seq` | SRA 下载、质控 (FastQC/fastp)、比对 (STAR)、定量 (Salmon)、差异表达 (DESeq2)、富集分析 (GO/KEGG) | 全自动流水线，一键生成 HTML 报告，自动参考基因组 |
| 📊**绘图工具**     | `packages/plot`    | 火山图、热图、PCA、柱状图（带误差棒/显著性标记）、折线图、饼图、染色体覆盖度图                   | Nature/Science 主题，支持中文，发表级质量        |
| 🧪**分子对接**     | `packages/docking` | 受体/配体准备、对接模拟配置及运行                                                                | 简化对接流程，提供统一的命令行接口               |
| 🛠️**核心组件**   | `packages/core`    | 日志管理、配置加载、子进程管理、文件 IO                                                          | 为所有模块提供底层通用能力支持                   |
| 🖥️**命令行入口** | `packages/cli`     | 统一 CLI 框架，插件加载，模板创建                                                                | 提供 `bioanalyze` 主命令，支持插件扩展         |

## 设计原则

- 模块独立发布、按需安装：每个工具模块是独立分发包，通过 entry points 注册 CLI 子命令
- 通用逻辑抽离：跨模块复用的功能统一沉淀到 `core`
- CLI 与 Python API 并行：同一能力既可命令行调用也可作为库导入

## 快速开始（开发态）

```powershell
uv venv
uv pip install -e packages/core -e packages/cli -e packages/transcriptome -e packages/docking
.\.venv\Scripts\bioanalyse.exe plugins
```

## 开发环境设置 (Development Setup)

为了保证代码质量和提交规范，本项目配置了 `pre-commit` 和 `commitizen`。

### 1. 安装开发工具

请确保在虚拟环境中安装了 `pre-commit`：

```bash
uv pip install pre-commit commitizen
```

### 2. 启用 Git Hooks

在项目根目录下运行：

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

### 3. 代码检查与提交

- **自动检查**：每次 `git commit` 时会自动运行代码格式化和检查。
- **手动检查**：运行 `pre-commit run --all-files` 检查所有文件。
- **规范提交**：建议使用 `cz commit` 来生成符合 Conventional Commits 规范的提交信息。

## 使用脚本一键安装 (Linux/macOS/WSL)

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

### 开发环境安装 (install.sh / install.bat)

如果您已经有环境或只想安装 Python 依赖（包括开发工具），可以使用安装脚本：

**Linux / macOS / WSL:**

```bash
bash install.sh
```

**Windows (PowerShell / CMD):**

```cmd
install.bat
```

此脚本会：

1. 检测并安装 `uv`（如果未安装）。
2. 创建 `.venv` 虚拟环境（如果不存在）。
3. 安装所有模块及 `pre-commit`, `commitizen`。
4. 自动配置 Git hooks。

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

### Docker 环境测试指南 (Running Tests in Docker)

对于 Windows 用户或不想在本地安装复杂依赖的开发者，我们提供了在 Docker 容器中运行测试的便捷方式。该环境会自动挂载本地代码、数据目录 (`data`) 和输出目录 (`output`)，因此：

1. 修改代码后无需重新构建镜像即可测试。
2. 测试代码可以直接访问 `data` 目录下的文件。
3. 测试生成的报告或文件可以直接在本地 `output` 目录查看。

**Windows (PowerShell):**

```powershell
.\run_tests_docker.ps1
```

**Linux / macOS:**

```bash
./run_tests_docker.sh
```

这将自动构建测试镜像并运行所有测试用例。

## 新增一个工具模块（约定）

1. 在 `packages/<module>/` 下创建独立包（`pyproject.toml` + `src/`）
2. 依赖公共模块：`bio-analyze-core`
3. 注册 CLI 插件入口：

```toml
[project.entry-points."bio_analyze.cli"]
<module> = "bio_analyze.<module>.cli:get_app"
```

4. 在 `bio_analyze.<module>.cli` 中实现 `get_app()` 并返回 `typer.Typer`

## 许可证 (License)

本项目采用 [GPL-3.0](LICENSE) 开源协议。
