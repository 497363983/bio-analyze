# Bio-Analyze Conda 构建配方

此目录包含用于将 `bio-analyze` 各个组件构建为独立 Conda 包的配方。

## 前置要求

1. **安装构建工具**:
   你需要安装 `conda-build` 来构建包，以及 `anaconda-client` 来上传包。

   ```bash
   conda install conda-build anaconda-client
   ```

2. **Anaconda 账号**:
   如果你还没有账号，请在 [Anaconda.org](https://anaconda.org/) 创建一个。
3. **登录**:

   ```bash
   anaconda login
   ```

## 1. 构建包

运行提供的 PowerShell 脚本，按正确的依赖顺序构建所有包：

```powershell
.\build_conda.ps1
```

或者手动构建（注意顺序！）：

```bash
# 1. Core (核心库)
conda build conda_recipes/bio-analyze-core -c conda-forge -c bioconda

# 2. Plot (依赖 core)
conda build conda_recipes/bio-analyze-plot -c conda-forge -c bioconda

# 3. Docking (依赖 core)
conda build conda_recipes/bio-analyze-docking -c conda-forge -c bioconda

# 4. Omics (依赖 core, plot)
conda build conda_recipes/bio-analyze-omics -c conda-forge -c bioconda

# 5. CLI (依赖 core)
conda build conda_recipes/bio-analyze-cli -c conda-forge -c bioconda
```

## 2. 发布（上传）到 Anaconda Cloud

构建完成后，包将位于你的本地 `conda-bld` 目录中（Windows 上通常是 `<conda_root>/conda-bld/win-64/`）。

你可以使用 `anaconda upload` 命令上传它们。

**自动上传脚本（推荐）**:
你可以使用以下命令查找并上传所有构建好的包：

```powershell
# 从构建目录上传所有 bio-analyze 包
anaconda upload (Get-ChildItem -Path $env:CONDA_PREFIX\conda-bld\win-64\bio-analyze-*.tar.bz2).FullName
```

**手动上传**:

```bash
anaconda upload <path_to_conda_bld>/win-64/bio-analyze-core-0.1.0-py_0.tar.bz2
anaconda upload <path_to_conda_bld>/win-64/bio-analyze-plot-0.1.0-py_0.tar.bz2
anaconda upload <path_to_conda_bld>/win-64/bio-analyze-docking-0.1.0-py_0.tar.bz2
anaconda upload <path_to_conda_bld>/win-64/bio-analyze-omics-0.1.0-py_0.tar.bz2
anaconda upload <path_to_conda_bld>/win-64/bio-analyze-cli-0.1.0-py_0.tar.bz2
```

## 3. 用户安装

上传后，用户可以通过指定你的频道来安装这些包：

```bash
# 将 <your-username> 替换为你的 Anaconda 用户名
conda install -c <your-username> -c conda-forge -c bioconda bio-analyze-cli
```

安装 `bio-analyze-cli` 会自动拉取 `bio-analyze-core`。其他插件（docking, plot, omics）可以按需安装：

```bash
conda install -c <your-username> -c conda-forge -c bioconda bio-analyze-docking
```
