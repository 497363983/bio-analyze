from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .base import save_plot
from .scatter import ScatterPlot


class PCAPlot(ScatterPlot):
    """
    PCA plot implementation.
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        hue: str | None = None,  # 分组列或值列表
        index_col: str | None = None,  # 用作索引的列
        transpose: bool = True,  # 默认为 True，适用于表达矩阵（基因 x 样本）
        n_components: int = 2,
        cluster: bool = False,  # 是否在组周围绘制置信椭圆
        n_clusters: int = 3,  # 未用于椭圆，但为兼容性保留。实际上我们使用 hue 分组。
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str = "pca.png",
        **kwargs: Any,
    ) -> Figure:
        """
        Generate PCA plot.

        Args:
            data:
                DataFrame containing numerical data.
            hue:
                Grouping info. Can be a column name in data when `transpose=False`,
                or a list/Series matching samples when `transpose=True`.
            index_col:
                Column to use as index (e.g. Gene ID).
            transpose:
                Whether to transpose the dataframe. Expression matrices are
                usually Gene x Sample, while PCA expects Sample x Gene.
            n_components:
                Number of components (default 2).
            cluster:
                If True, draw confidence ellipses around groups defined by hue.
            n_clusters:
                Deprecated/Ignored. Ellipses are drawn based on 'hue' grouping.
            title:
                Chart title.
            xlabel:
                X-axis label.
            ylabel:
                Y-axis label.
            output:
                Path to save the chart.
            **kwargs:
                Other arguments passed to ScatterPlot.
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("pca")

        # 合并参数
        for k, v in theme_params.items():
            if k not in kwargs:
                kwargs[k] = v

        # 准备数据
        df = data.copy()

        # 首先处理索引
        if index_col and index_col in df.columns:
            df = df.set_index(index_col)

        # 如果 transpose 为 False，我们假设是 样本 x 基因（Tidy 格式）。
        # Hue 可能是 df 中的一列。
        groups = None
        if not transpose and hue and isinstance(hue, str) and hue in df.columns:
            groups = df[hue]
            df = df.drop(columns=[hue])

        # 仅选择数值列
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            raise ValueError("No numeric data found for PCA.")

        # 如果需要，进行转置（基因 x 样本 -> 样本 x 基因）
        if transpose:
            numeric_df = numeric_df.T

        # 标准化
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(numeric_df)

        # PCA
        pca = PCA(n_components=n_components)
        x_pca = pca.fit_transform(x_scaled)

        # 创建绘图 dataframe
        plot_df = pd.DataFrame(
            data=x_pca,
            columns=[f"PC{i + 1}" for i in range(n_components)],
            index=numeric_df.index,
        )

        # 添加 hue 信息
        hue_col = None
        if groups is not None:
            # 情况 1：Hue 是原始 df 中的一列（transpose=False）
            plot_df[hue] = groups
            hue_col = hue
        elif hue is not None:
            # 情况 2：Hue 作为外部列表/序列提供（例如用于转置数据）
            # 检查长度
            if len(hue) == len(plot_df):
                if isinstance(hue, pd.Series) and hue.name:
                    hue_col = hue.name
                    plot_df[hue_col] = hue
                elif isinstance(hue, str):  # 如果 hue 是字符串但不在列中
                    # 回退或报错
                    pass
                else:
                    # 假设它是类列表
                    plot_df["Group"] = hue
                    hue_col = "Group"

        # 如果请求且未提供 hue，则自动聚类
        if cluster and hue_col is None:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
            clusters = kmeans.fit_predict(x_pca)
            hue_col = "Cluster"
            plot_df[hue_col] = [f"Cluster {c + 1}" for c in clusters]

        # 使用方差确定 x 和 y 标签
        var_ratio = pca.explained_variance_ratio_
        if xlabel is None:
            xlabel = f"PC1 ({var_ratio[0]:.2%})"
        if ylabel is None:
            ylabel = f"PC2 ({var_ratio[1]:.2%})"

        # 调用父类 ScatterPlot.plot
        # 注意：这里我们通过 add_ellipse 参数复用父类的椭圆绘制逻辑
        # PCA 的 cluster 参数现在对应 ScatterPlot 的 add_ellipse 参数

        # 传递给父类的 kwargs
        # 移除已处理的参数，避免传递冲突（虽然 kwargs 主要是给 seaborn 的）

        return super().plot(
            data=plot_df,
            x="PC1",
            y="PC2",
            hue=hue_col,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            add_ellipse=cluster and (hue_col is not None),
            # 其他 kwargs 透传给 ScatterPlot -> seaborn.scatterplot
            **kwargs,
        )
