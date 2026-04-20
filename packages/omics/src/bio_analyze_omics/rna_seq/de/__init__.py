from pathlib import Path

import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)


class DEManager:
    """Differential expression analysis manager."""

    def __init__(self, counts: pd.DataFrame, design_file: Path, output_dir: Path, theme: str = "default"):
        """
        Initialize the differential expression analysis manager.

        Args:
            counts (pd.DataFrame): Counts matrix with genes as rows and samples as columns.
            design_file (Path): Path to the experimental design CSV file.
            output_dir (Path): Path to the output directory.
            theme (str, optional): Plotting theme.
        """
        self.counts = counts
        self.design_file = Path(design_file)
        self.output_dir = output_dir
        self.theme = theme
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> pd.DataFrame:
        """
        Run differential expression analysis with DESeq2.

        Returns:
            pd.DataFrame: Differential expression results.

        Raises:
            ValueError: If the design file is missing the `sample` column,
                there are no matching samples, or there are fewer than
                two conditions.
        """
        # 加载实验设计
        design = pd.read_csv(self.design_file)

        # 确保 'sample' 列存在
        if "sample" not in design.columns:
            raise ValueError("Design file must have a 'sample' column.")

        design.set_index("sample", inplace=True)

        # 过滤样本以匹配计数矩阵
        common_samples = list(set(self.counts.columns) & set(design.index))
        if not common_samples:
            raise ValueError("No matching samples between counts and design file.")

        counts_subset = self.counts[common_samples].T  # PyDESeq2 需要样本作为行
        design_subset = design.loc[common_samples]

        # 假设用于差异表达的列名为 'condition'
        if "condition" not in design_subset.columns:
            # 尝试选择第一个非样本列
            condition_col = design_subset.columns[0]
            logger.warning(f"'condition' column not found. Using '{condition_col}' as condition.")
        else:
            condition_col = "condition"

        # 运行 DESeq2
        logger.info(f"Running DESeq2 on {len(common_samples)} samples using condition '{condition_col}'...")

        dds = DeseqDataSet(
            counts=counts_subset,
            metadata=design_subset,
            design_factors=condition_col,
            refit_cooks=True,
            n_cpus=4,
        )

        dds.deseq2()

        # 运行统计检验 (对比)
        # 获取水平
        levels = design_subset[condition_col].unique()
        if len(levels) < 2:
            raise ValueError("Need at least 2 conditions for DE analysis.")

        # 默认对比: Level[1] vs Level[0] (例如 Treated vs Control，如果 Control 按字母顺序排在前面)
        # 理想情况下用户指定，但目前取排序后的结果
        levels = sorted(levels)
        contrast = [condition_col, levels[1], levels[0]]
        logger.info(f"Contrasting {levels[1]} vs {levels[0]}")

        stat_res = DeseqStats(dds, contrast=contrast, n_cpus=4)
        stat_res.summary()

        # 获取结果
        res_df = stat_res.results_df

        # 保存结果
        res_path = self.output_dir / "deseq2_results.csv"
        res_df.to_csv(res_path)

        # 同时保存归一化计数
        # norm_counts = dds.layers["log1p"]  # 或 dds.layers['normed_counts']?
        # pydeseq2 可能以不同方式存储归一化计数。
        # 可以使用 dds.vst()。
        # 暂时只保存结果。

        return res_df
