import json
import shutil
from pathlib import Path

import pandas as pd

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run as run_command

logger = get_logger(__name__)


class QuantManager:
    """
    zh: 定量分析管理器。
    en: Quantification analysis manager.
    """

    def __init__(self, reads: dict, reference: dict, output_dir: Path, threads: int = 4):
        """
        zh: 初始化定量分析管理器。
        en: Initialize the quantification analysis manager.

        Args:
            reads (dict):
                zh: 样本读取文件字典。
                en: Dictionary of sample read files.
            reference (dict):
                zh: 参考基因组文件字典（包含 'fasta' 和可选的 'gtf'）。
                en: Dictionary of reference genome files (contains 'fasta' and optional 'gtf').
            output_dir (Path):
                zh: 输出目录路径。
                en: Path to the output directory.
            threads (int, optional):
                zh: 使用的线程数。
                en: Number of threads to use.
        """
        self.reads = reads
        self.reference = reference
        self.output_dir = output_dir
        self.threads = threads
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir = self.output_dir / "salmon_index"

    def run(self) -> pd.DataFrame:
        """
        zh: 运行 Salmon 定量流程。
        en: Run the Salmon quantification workflow.

        zh: 1. 检查 salmon
        en: 1. Check salmon
        zh: 2. 构建索引
        en: 2. Build index
        zh: 3. 定量每个样本
        en: 3. Quantify each sample
        zh: 4. 合并计数
        en: 4. Merge counts

        Returns:
            pd.DataFrame:
                zh: 合并后的计数矩阵。
                en: Merged counts matrix.

        Raises:
            RuntimeError:
                zh: 如果未找到 Salmon。
                en: If Salmon is not found.
        """
        # 1. 检查 salmon
        if not shutil.which("salmon"):
            raise RuntimeError("Salmon not found in PATH.")

        # 2. 构建索引
        self._build_index()

        # 3. 定量每个样本
        quant_files = {}
        for sample, files in self.reads.items():
            out_path = self.output_dir / sample
            self._quantify_sample(sample, files, out_path)
            quant_files[sample] = out_path / "quant.sf"

        # 4. 合并计数
        return self._merge_counts(quant_files)

    def _build_index(self):
        """
        zh: 构建 Salmon 索引。
        en: Build Salmon index.
        """
        if self.index_dir.exists():
            logger.info("Salmon index already exists. Skipping build.")
            return

        fasta = self.reference.get("fasta")
        gtf = self.reference.get("gtf")

        transcript_fasta = self.output_dir / "transcripts.fa"

        if shutil.which("gffread") and gtf:
            logger.info("Extracting transcripts with gffread...")
            cmd = ["gffread", "-w", str(transcript_fasta), "-g", str(fasta), str(gtf)]
            run_command(cmd, check=True)
        else:
            logger.warning("gffread not found or GTF missing. Assuming provided FASTA is transcriptome.")
            transcript_fasta = fasta

        logger.info("Building Salmon index...")
        cmd = [
            "salmon",
            "index",
            "-t",
            str(transcript_fasta),
            "-i",
            str(self.index_dir),
            "-p",
            str(self.threads),
        ]
        run_command(cmd, check=True)

    def _quantify_sample(self, sample: str, files: dict, out_dir: Path):
        """
        zh: 定量单个样本。
        en: Quantify a single sample.

        Args:
            sample (str):
                zh: 样本名称。
                en: Sample name.
            files (dict):
                zh: 样本文件字典。
                en: Sample files dictionary.
            out_dir (Path):
                zh: 输出目录路径。
                en: Output directory path.
        """
        if out_dir.exists():
            logger.info(f"Sample {sample} already quantified.")
            return

        cmd = [
            "salmon",
            "quant",
            "-i",
            str(self.index_dir),
            "-l",
            "A",  # 自动检测文库类型
            "-o",
            str(out_dir),
            "-p",
            str(self.threads),
            "--validateMappings",
        ]

        if "R2" in files:
            cmd.extend(["-1", str(files["R1"]), "-2", str(files["R2"])])
        else:
            cmd.extend(["-r", str(files["R1"])])

        run_command(cmd, check=True)

    def _merge_counts(self, quant_files: dict) -> pd.DataFrame:
        """
        zh: 合并定量结果。
        en: Merge quantification results.

        Args:
            quant_files (dict):
                zh: 样本名称到 quant.sf 文件路径的字典。
                en: Dictionary mapping sample names to quant.sf file paths.

        Returns:
            pd.DataFrame:
                zh: 合并后的计数矩阵。
                en: Merged counts matrix.
        """
        logger.info("Merging quantification results...")
        counts = {}
        for sample, path in quant_files.items():
            df = pd.read_csv(path, sep="\t", index_col=0)
            counts[sample] = df["NumReads"]  # 使用原始计数进行 DE 分析

        count_matrix = pd.DataFrame(counts)
        count_matrix = count_matrix.fillna(0).astype(int)

        # 保存矩阵
        count_matrix.to_csv(self.output_dir / "counts.csv")
        return count_matrix

    def get_stats(self) -> dict:
        """
        zh: 从 Salmon 输出中提取比对率。
        en: Extract mapping rate from Salmon output.

        Returns:
            dict:
                zh: {sample: mapping_rate (float)}
                en: {sample: mapping_rate (float)}
        """
        stats = {}
        for sample_dir in self.output_dir.iterdir():
            if sample_dir.is_dir() and (sample_dir / "aux_info" / "meta_info.json").exists():
                try:
                    with open(sample_dir / "aux_info" / "meta_info.json") as f:
                        data = json.load(f)
                        stats[sample_dir.name] = data.get("percent_mapped", 0.0)
                except Exception as e:
                    logger.warning(f"Failed to parse Salmon stats for {sample_dir.name}: {e}")
        return stats
