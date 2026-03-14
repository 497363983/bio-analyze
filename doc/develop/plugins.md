# Plugin Development

## Create New Project/Template

Use the `create` command to quickly generate a standard project structure.

### Interactive Creation

```bash
bioanalyze create
```

(Then follow the prompts to select the type and enter the name)

### Quickly Create New Tool

```bash
bioanalyze create tool --name my-new-tool
```

This will generate a new analysis module template under `packages/my-new-tool`.

### Quickly Create Plotting Theme

```bash
bioanalyze create theme --name my-company-theme
```

This will generate a Python package named `my-company-theme` in the current directory, where you can modify `__init__.py` to customize `bio-plot` styles.

## Add New Module

1. Use `bioanalyze create tool` to create a template.
2. Configure `[project.entry-points."bio_analyze.plugins"]` in `pyproject.toml`.
3. Implement the `get_app()` function to return a `typer.Typer` instance.
4. Run `uv sync` to install the new module.
5. Now you can call your new tool via `bioanalyze <tool-name>`.
