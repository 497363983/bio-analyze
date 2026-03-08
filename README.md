# bio-analyze

一个面向常用生物信息学分析任务的工具箱，采用 monorepo 组织多个独立模块，最终可通过统一 CLI 与 Python API 调用。

## Monorepo 结构

- `packages/core`：公共能力（配置、日志、IO、运行外部命令、资源管理等）
- `packages/cli`：统一命令行入口，支持插件式加载各模块子命令
- `packages/*`：各分析工具模块（例如 transcriptome、docking），每个模块是独立可发布包

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

## 新增一个工具模块（约定）

1. 在 `packages/<module>/` 下创建独立包（`pyproject.toml` + `src/`）
2. 依赖公共模块：`bio-analyze-core`
3. 注册 CLI 插件入口：

```toml
[project.entry-points."bio_analyze.cli"]
<module> = "bio_analyze.<module>.cli:get_app"
```

4. 在 `bio_analyze.<module>.cli` 中实现 `get_app()` 并返回 `typer.Typer`
