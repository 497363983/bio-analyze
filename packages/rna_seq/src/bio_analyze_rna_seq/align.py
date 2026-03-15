import shutil
from pathlib import Path

import pandas as pd
from bio_analyze_plot.plots.chromosome import ChromosomePlot

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run as run_command

logger = get_logger(__name__)


class StarAlignmentManager:
    def __init__(
        self,
        reads: dict,
        reference: dict,
        output_dir: Path,
        threads: int = 4,
        star_index_dir: Path | None = None,
        theme: str = "default",
    ):
        self.reads = reads
        self.reference = reference
        self.output_dir = output_dir
        self.threads = threads
        self.star_index_dir = star_index_dir or output_dir / "star_index"
        self.theme = theme
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.star_index_dir.mkdir(parents=True, exist_ok=True)

    def check_star(self):
        """检查 STAR 是否可用。"""
        if not shutil.which("STAR"):
            raise RuntimeError("STAR not found in PATH.")
        if not shutil.which("samtools"):
            raise RuntimeError("samtools not found in PATH (required for indexing stats).")

    def run(self) -> dict[str, Path]:
        """
        运行 STAR 比对流程。
        1. 检查/构建索引
        2. 比对
        3. 统计染色体分布
        4. 绘图
        返回 BAM 文件路径字典。
        """
        self.check_star()

        # 1. 构建索引
        self._build_index()

        # 2. 比对
        bam_files = {}
        for sample, files in self.reads.items():
            out_prefix = self.output_dir / f"{sample}_"
            bam_file = self._align_sample(sample, files, out_prefix)
            bam_files[sample] = bam_file

            # 3. 统计和绘图
            self._process_bam_stats(sample, bam_file)

        return bam_files

    def _build_index(self):
        """构建 STAR 索引。"""
        # 检查索引是否已存在（简单的检查：SA 文件存在）
        if (self.star_index_dir / "SA").exists():
            logger.info("STAR index already exists. Skipping build.")
            return

        fasta = self.reference.get("fasta")
        gtf = self.reference.get("gtf")

        if not fasta:
            raise ValueError("Reference FASTA is required for STAR alignment.")

        logger.info("Building STAR index...")
        cmd = [
            "STAR",
            "--runMode",
            "genomeGenerate",
            "--genomeDir",
            str(self.star_index_dir),
            "--genomeFastaFiles",
            str(fasta),
            "--runThreadN",
            str(self.threads),
        ]

        if gtf:
            cmd.extend(["--sjdbGTFfile", str(gtf)])

        # 针对小基因组优化（可选，这里暂不自动处理，假设是常规基因组）
        # 如果 genomeSAindexNbases 默认值对于小基因组太大，STAR 会报错。
        # 但我们先假设用户使用的是标准物种。

        try:
            run_command(cmd, check=True)
        except Exception as e:
            logger.error(f"Failed to build STAR index: {e}")
            raise

    def _align_sample(self, sample: str, files: dict, out_prefix: Path) -> Path:
        """比对单个样本。"""
        # STAR 输出文件名
        # Aligned.sortedByCoord.out.bam
        final_bam = Path(f"{out_prefix}Aligned.sortedByCoord.out.bam")

        if final_bam.exists():
            logger.info(f"Sample {sample} already aligned. Skipping.")
            return final_bam

        logger.info(f"Aligning sample {sample} with STAR...")

        cmd = [
            "STAR",
            "--genomeDir",
            str(self.star_index_dir),
            "--runThreadN",
            str(self.threads),
            "--readFilesCommand",
            "zcat",  # 假设输入是 .gz
            "--outFileNamePrefix",
            str(out_prefix),
            "--outSAMtype",
            "BAM",
            "SortedByCoordinate",
            "--outSAMunmapped",
            "Within",
            "--outSAMattributes",
            "Standard",
        ]

        if "R2" in files:
            cmd.extend(["--readFilesIn", str(files["R1"]), str(files["R2"])])
        else:
            cmd.extend(["--readFilesIn", str(files["R1"])])

        try:
            run_command(cmd, check=True)
            # 建立索引
            run_command(["samtools", "index", str(final_bam)], check=True)
        except Exception as e:
            logger.error(f"STAR alignment failed for {sample}: {e}")
            raise

        return final_bam

    def _process_bam_stats(self, sample: str, bam_file: Path):
        """统计 BAM 文件的染色体覆盖度分布并绘图（分链）。"""
        logger.info(f"Calculating chromosome coverage for {sample}...")

        # 1. 获取染色体长度信息
        idxstats_res = run_command(["samtools", "idxstats", str(bam_file)], check=True)
        chrom_lengths = {}
        for line in idxstats_res.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0] != "*":
                chrom_lengths[parts[0]] = int(parts[1])

        # 2. 选择主要染色体（避免处理成千上万个 contigs）
        # 策略：按长度排序，取前 50 个
        sorted_chroms = sorted(chrom_lengths.items(), key=lambda x: x[1], reverse=True)[:50]
        target_chroms = {c[0]: c[1] for c in sorted_chroms}

        # 3. 计算覆盖度 (使用 binning)
        # bin size 设为 100kb
        bin_size = 100000

        # 初始化 bins 数据结构
        # {(chrom, bin_idx): {'pos': 0, 'neg': 0}}
        bins_data = {}

        # 使用 samtools view 流式读取
        # 只读取 target_chroms 中的 reads
        # -F 4 (mapped), -F 256 (not primary alignment, optional but good to avoid double counting)
        # 我们只关心主要的 mapped reads
        # 也可以加上 -q 30 过滤低质量比对

        # 为了效率，我们只提取需要的列: FLAG, RNAME, POS
        # 注意: samtools view 输出默认包含这些。
        # 我们可以用 cut 命令减少数据传输量，但为了跨平台兼容性，直接在 python 中处理。

        # 构建 samtools 命令
        cmd = ["samtools", "view", "-F", "260", str(bam_file)]  # -F 260 = unmapped (4) + secondary (256)

        # 运行命令并处理输出流
        import subprocess

        try:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1024 * 1024) as proc:
                for line in proc.stdout:
                    parts = line.split("\t")
                    if len(parts) < 4:
                        continue

                    flag = int(parts[1])
                    chrom = parts[2]
                    pos = int(parts[3])

                    if chrom not in target_chroms:
                        continue

                    # 计算 bin index
                    bin_idx = pos // bin_size
                    key = (chrom, bin_idx)

                    if key not in bins_data:
                        bins_data[key] = {"pos": 0, "neg": 0}

                    # 判断链方向
                    # 对于双端测序，判断链比较复杂。
                    # 通常:
                    # R1 (read1):
                    #   - 16 set (reverse strand) -> 基因在负链 (如果是 dUTP/stranded 协议，可能反过来)
                    #   - 16 unset -> 基因在正链
                    # R2 (read2): 反之
                    # 这里简化处理：直接使用 FLAG 16 判断 read 的比对方向。
                    # 16 set: reverse strand (-)
                    # 16 unset: forward strand (+)
                    is_reverse = (flag & 16) != 0

                    if is_reverse:
                        bins_data[key]["neg"] += 1
                    else:
                        bins_data[key]["pos"] += 1

        except Exception as e:
            logger.error(f"Error calculating coverage: {e}")
            return

        # 转换为 DataFrame
        rows = []
        for (chrom, bin_idx), counts in bins_data.items():
            rows.append(
                {"chrom": chrom, "pos": bin_idx * bin_size, "counts_pos": counts["pos"], "counts_neg": counts["neg"]}
            )

        if not rows:
            logger.warning(f"No coverage data found for {sample}")
            return

        df = pd.DataFrame(rows)

        # 绘图
        plot_out = self.output_dir / f"{sample}_chrom_dist.png"
        plotter = ChromosomePlot(theme=self.theme)
        plotter.plot(
            data=df,
            chrom_col="chrom",
            pos_col="pos",
            pos_counts_col="counts_pos",
            neg_counts_col="counts_neg",
            title=f"Reads Coverage Distribution - {sample}",
            output=str(plot_out),
            bin_size=bin_size,
            max_chroms=30,
        )
