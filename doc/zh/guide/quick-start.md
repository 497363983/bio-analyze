# 快速开始

## 快速开始（开发态）

```powershell
uv venv
uv pip install -e packages/core -e packages/cli -e packages/transcriptome -e packages/docking
.\.venv\Scripts\bioanalyse.exe plugins
```

## Docker 环境测试指南 (Running Tests in Docker)

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
