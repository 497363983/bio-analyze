# 插件开发

## 创建新项目/模版

使用 `create` 命令可以快速生成标准的项目结构。

### 交互式创建

```bash
bioanalyze create
```

（随后根据提示选择类型和输入名称）

### 快速创建新工具

```bash
bioanalyze create tool --name my-new-tool
```

这将在 `packages/my-new-tool` 下生成一个新的分析模块模版。

### 快速创建绘图主题

```bash
bioanalyze create theme --name my-company-theme
```

这将在当前目录下生成一个名为 `my-company-theme` 的 Python 包，您可以修改其中的 `__init__.py` 来定制 `bio-plot` 的样式。

## 添加新模块

1. 使用 `bioanalyze create tool` 创建模版。
2. 在 `pyproject.toml` 中配置 `[project.entry-points."bio_analyze.plugins"]`。
3. 实现 `get_app()` 函数返回 `typer.Typer` 实例。
4. 运行 `uv sync` 安装新模块。
5. 现在可以通过 `bioanalyze <tool-name>` 调用您的新工具了。
