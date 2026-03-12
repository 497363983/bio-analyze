from typing import Any

import matplotlib.transforms as transforms
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .base import BasePlot, save_plot


def confidence_ellipse(x, y, ax, n_std=2.0, facecolor="none", **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2, facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D().rotate_deg(45).scale(scale_x, scale_y).translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


class PCAPlot(BasePlot):
    """
    PCA 图实现。
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        x: str | None = None,  # 未使用
        y: str | None = None,  # 未使用
        hue: str | None = None,  # 分组列或值列表
        index_col: str | None = None,  # 用作索引的列
        transpose: bool = True,  # 默认为 True，适用于表达矩阵（基因 x 样本）
        n_components: int = 2,
        cluster: bool = False,  # 是否在组周围绘制置信椭圆
        n_clusters: int = 3,  # 未用于椭圆，但为兼容性保留。实际上我们使用 hue 分组。
        title: str | None = None,  # 移回显式参数列表以修复 NameError
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str = "pca.png",
        **kwargs: Any,
    ) -> Figure:
        """
        生成 PCA 图。

        Args:
            data: 包含数值数据的 DataFrame。
            hue: 分组信息。可以是 data 中的列名（如果 transpose=False），
                 或者是与样本匹配的值列表/Series（如果 transpose=True）。
            index_col: 用作索引的列（例如基因 ID）。
            transpose: 是否转置 dataframe。
                       通常表达矩阵是 基因 x 样本。
                       PCA 需要 样本 x 基因。所以默认为 True。
            n_components: 组件数量（默认 2）。
            cluster: 如果为 True，则围绕 hue 定义的组绘制置信椭圆。
            n_clusters: 已弃用/忽略。椭圆是基于 'hue' 分组绘制的。
            xlabel: X轴标签。
            ylabel: Y轴标签。
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("pca")

        # 合并参数
        # s (size) 是常见的 seaborn 参数
        s = kwargs.get("s", theme_params.get("s", None))
        if s is not None:
            kwargs["s"] = s

        # 处理 palette: kwargs > theme_params > 自动生成
        palette = kwargs.get("palette", theme_params.get("palette", None))
        if palette is not None:
            kwargs["palette"] = palette

        # 椭圆样式参数
        ellipse_kws = kwargs.get("ellipse_kws", theme_params.get("ellipse_kws", {}))
        # 默认椭圆 alpha
        if "alpha" not in ellipse_kws:
            ellipse_kws["alpha"] = 0.1

        fig, ax = self.get_fig_ax()

        # 准备数据
        df = data.copy()

        # 首先处理索引
        if index_col and index_col in df.columns:
            df = df.set_index(index_col)

        # 如果 transpose 为 False，我们假设是 样本 x 基因（Tidy 格式）。
        # Hue 可能是 df 中的一列。
        groups = None
        if not transpose:
            if hue and isinstance(hue, str) and hue in df.columns:
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
        X_scaled = scaler.fit_transform(numeric_df)

        # PCA
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)

        # 创建绘图 dataframe
        plot_df = pd.DataFrame(data=X_pca, columns=[f"PC{i + 1}" for i in range(n_components)], index=numeric_df.index)

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
                col_name = "Group"
                if isinstance(hue, pd.Series) and hue.name:
                    col_name = hue.name
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
            clusters = kmeans.fit_predict(X_pca)
            hue_col = "Cluster"
            plot_df[hue_col] = [f"Cluster {c + 1}" for c in clusters]

        # 聚类 / 椭圆
        if cluster and hue_col:
            # 为每组绘制置信椭圆
            # 我们需要访问调色板以使椭圆颜色与点匹配

            # 获取唯一组
            unique_groups = plot_df[hue_col].unique()

            # 如果未提供，手动创建调色板以确保持致性
            palette = None
            if "palette" in kwargs:
                palette = kwargs["palette"]
            else:
                # 从 seaborn 获取默认调色板
                # 这很棘手，因为如果我们不提供调色板映射，seaborn 会在内部全分配颜色
                # 但我们可以生成一个。
                n_colors = len(unique_groups)
                colors = sns.color_palette(n_colors=n_colors)
                palette = dict(zip(unique_groups, colors))
                # 稍后将此调色板传递给 scatterplot 以确保匹配
                kwargs["palette"] = palette

            for group in unique_groups:
                group_data = plot_df[plot_df[hue_col] == group]
                if len(group_data) < 3:
                    # 至少需要 3 个点来绘制椭圆？实际上 2 个可能行，但 3 个对方差更安全
                    continue

                # 绘制椭圆
                # 获取颜色
                color = palette[group] if isinstance(palette, dict) else None

                # 准备椭圆参数
                final_ellipse_kws = ellipse_kws.copy()
                if "facecolor" not in final_ellipse_kws:
                    final_ellipse_kws["facecolor"] = color

                # 绘制填充椭圆
                confidence_ellipse(
                    group_data["PC1"],
                    group_data["PC2"],
                    ax,
                    n_std=2.0,
                    edgecolor="none",  # 填充无边缘
                    zorder=0,  # 在点后面
                    **final_ellipse_kws,
                )
                # 绘制轮廓
                final_outline_kws = ellipse_kws.copy()
                # 移除填充相关的参数
                if "alpha" in final_outline_kws:
                    del final_outline_kws["alpha"]
                if "facecolor" in final_outline_kws:
                    del final_outline_kws["facecolor"]

                confidence_ellipse(
                    group_data["PC1"],
                    group_data["PC2"],
                    ax,
                    n_std=2.0,
                    edgecolor=color,
                    facecolor="none",
                    linestyle="--",
                    linewidth=1,
                    zorder=0,
                )

        # 使用方差确定 x 和 y 标签
        var_ratio = pca.explained_variance_ratio_
        xlabel = f"PC1 ({var_ratio[0]:.2%})"
        ylabel = f"PC2 ({var_ratio[1]:.2%})"

        sns.scatterplot(
            data=plot_df,
            x="PC1",
            y="PC2",
            hue=hue_col,
            ax=ax,
            **{
                k: v for k, v in kwargs.items() if k not in ["title", "ellipse_kws", "palette"]
            },  # 避免将 title, ellipse_kws, palette 传递给 scatterplot (palette 单独传或者已经在 kwargs 中？)
            palette=kwargs.get("palette"),  # 显式传递 palette
        )

        if title:
            ax.set_title(title)  # 显式设置标题

        if xlabel:
            ax.set_xlabel(xlabel)
        else:
            ax.set_xlabel(f"PC1 ({var_ratio[0]:.2%})")

        if ylabel:
            ax.set_ylabel(ylabel)
        else:
            ax.set_ylabel(f"PC2 ({var_ratio[1]:.2%})")

        return fig
