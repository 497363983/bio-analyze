---
---

# Theme Chart-Specific Parameters

This page summarizes all chart keys supported by `chart_specific_params` in plot theme/config files.

## Supported Chart Keys

- `bar`
- `box`
- `chromosome`
- `gsea`
- `heatmap`
- `line`
- `msa`
- `pca`
- `pie`
- `scatter`
- `tree`
- `volcano`

## Configuration Example

```json
{
  "name": "my_theme",
  "chart_specific_params": {
    "bar": {
      "palette": "Set2",
      "err_color": "#222222",
      "cap_color": "#222222"
    },
    "msa": {
      "seq_type": "aa",
      "show_logo": false,
      "bases_per_line": 60,
      "rc_params": {
        "axes.facecolor": "#f7f7f7"
      },
      "base_colors": {
        "A": "#111111",
        "-": "#f8f8f8"
      }
    },
    "volcano": {
      "alpha": 0.8,
      "s": 18,
      "cutoff_line_kws": {
        "color": "grey",
        "linestyle": "--",
        "linewidth": 0.8
      }
    }
  }
}
```

`rc_params` can be configured per chart under each chart key. It is applied only while rendering that chart and does not leak to other charts.

## Per-Chart Parameter Summary

### `bar`

- Common keys: `palette`, `err_color`, `cap_color`
- Also supports additional `seaborn.barplot()` kwargs.
- Supports per-chart `rc_params`.

### `box`

- Common keys: `palette`
- Also supports additional `seaborn.boxplot()` kwargs.
- Supports per-chart `rc_params`.

### `chromosome`

- Common keys: `color_pos`, `color_neg`, `label_pos`, `label_neg`, `zero_line_kws`
- Supports per-chart `rc_params`.

### `gsea`

- Common keys: `color`, `hit_color`, `show_border`
- Supports per-chart `rc_params`.

### `heatmap`

- Uses `chart_specific_params.heatmap` as base kwargs for `seaborn.clustermap()`.
- Common keys: `cmap`, `center` and any valid `clustermap` kwargs.
- Supports per-chart `rc_params`.

### `line`

- Merges `chart_specific_params.line` into plotting kwargs.
- Common keys: `palette`, `markers`, `dashes` and other `seaborn.lineplot()` kwargs.
- Supports per-chart `rc_params`.

### `msa`

- Common keys: `seq_type`, `show_logo`, `font_size`, `figsize`, `bases_per_line`, `base_colors`
- Supports per-chart `rc_params`.

### `pca`

- Merges `chart_specific_params.pca` into downstream scatter kwargs.
- Common keys: `palette`, `s`, `alpha`, `ellipse_kws` and other scatter kwargs.
- Supports per-chart `rc_params`.

### `pie`

- Common keys: `colors`, `palette`
- Supports per-chart `rc_params`.

### `scatter`

- Common keys: `palette`, `s`, `ellipse_kws`
- Also supports additional `seaborn.scatterplot()` kwargs.
- Supports per-chart `rc_params`.

### `tree`

- Common keys: `color`, `label_offset_scale`, `label_bbox_alpha`
- Supports per-chart `rc_params`.

### `volcano`

- Common keys: `alpha`, `s`, `cutoff_line_kws`, `labels`, `palette`
- Supports per-chart `rc_params`.

## Parameter Priority

In all charts, runtime arguments passed to `plot()` have higher priority than theme defaults in `chart_specific_params`.
