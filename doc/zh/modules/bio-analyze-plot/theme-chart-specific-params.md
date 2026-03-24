---
---

# 主题图表参数总览

本页汇总 `chart_specific_params` 在绘图主题/配置文件中的支持范围与推荐写法。

## 支持的图表键

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

## 配置示例

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

每个图表键下均可配置 `rc_params`。该配置只在当前图表绘制期间生效，不会泄露到其他图表。

## 各图可配置参数

### `bar`

- 常用键：`palette`、`err_color`、`cap_color`
- 同时支持其他 `seaborn.barplot()` 参数。
- 支持图级 `rc_params`。

### `box`

- 常用键：`palette`
- 同时支持其他 `seaborn.boxplot()` 参数。
- 支持图级 `rc_params`。

### `chromosome`

- 常用键：`color_pos`、`color_neg`、`label_pos`、`label_neg`、`zero_line_kws`
- 支持图级 `rc_params`。

### `gsea`

- 常用键：`color`、`hit_color`、`show_border`
- 支持图级 `rc_params`。

### `heatmap`

- `chart_specific_params.heatmap` 会作为 `seaborn.clustermap()` 的基础参数。
- 常用键：`cmap`、`center` 以及其他合法 `clustermap` 参数。
- 支持图级 `rc_params`。

### `line`

- `chart_specific_params.line` 会并入绘图参数。
- 常用键：`palette`、`markers`、`dashes` 以及其他 `seaborn.lineplot()` 参数。
- 支持图级 `rc_params`。

### `msa`

- 常用键：`seq_type`、`show_logo`、`font_size`、`figsize`、`bases_per_line`、`base_colors`
- 支持图级 `rc_params`。

### `pca`

- `chart_specific_params.pca` 会并入下游散点图参数。
- 常用键：`palette`、`s`、`alpha`、`ellipse_kws` 以及其他散点图参数。
- 支持图级 `rc_params`。

### `pie`

- 常用键：`colors`、`palette`
- 支持图级 `rc_params`。

### `scatter`

- 常用键：`palette`、`s`、`ellipse_kws`
- 同时支持其他 `seaborn.scatterplot()` 参数。
- 支持图级 `rc_params`。

### `tree`

- 常用键：`color`、`label_offset_scale`、`label_bbox_alpha`
- 支持图级 `rc_params`。

### `volcano`

- 常用键：`alpha`、`s`、`cutoff_line_kws`、`labels`、`palette`
- 支持图级 `rc_params`。

## 参数优先级

所有图类型均遵循：`plot()` 显式传参优先于 `chart_specific_params` 主题默认值。
