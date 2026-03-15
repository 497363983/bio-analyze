# bio-analyze-plot

**bio-analyze-plot** is a professional plotting module within the `bio-analyze` toolkit. Built on `matplotlib` and `seaborn`, it generates various bioinformatics statistical charts and supports flexible theme customization.

## ✨ Features

- **Customizable Themes**: Provides built-in themes (Nature/Science) as a base, while supporting full customization of fonts, sizes, line widths, and color schemes.
- **Wide Data Support**: Supports `.csv`, `.tsv`, `.txt`, `.xlsx`, and `.xls` formats, with `--sheet` option for Excel worksheets.
- **Multi-format Export**: Supports `png`, `pdf`, `svg`, `jpg`, `tiff`, and more.
- **Chinese Comments**: Code comments are in Chinese, facilitating understanding and secondary development for developers.
- **LaTeX Support**: Automatically parses LaTeX formulas in axis labels (e.g., `$y = \sin(x)$`).
- **Unified CLI**: All charts can be invoked through a unified command-line interface.

## 🎨 Themes

Supports custom plotting themes via JSON files or Python code.

### Using Built-in Themes

```bash
# Use Nature style
bio-analyze plot volcano result.csv --theme nature

# Use Science style
bio-analyze plot volcano result.csv --theme science
```

### Custom Theme (JSON)

Create `my_theme.json`:

```json
{
  "name": "dark_presentation",
  "style": "darkgrid",
  "context": "talk",
  "font": "Arial",
  "rc_params": {
    "lines.linewidth": 2.5,
    "axes.labelsize": 14
  }
}
```

Usage: `bio-analyze plot volcano ... --theme ./my_theme.json`

## 💻 Development

Unit test outputs are located in the `packages/plot/tests/output` directory.

```bash
pytest packages/plot/tests
```
