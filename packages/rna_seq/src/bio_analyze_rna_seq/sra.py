import shutil
from pathlib import Path

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run as run_command

logger = get_logger(__name__)


class SRAManager:
    def __init__(self, output_dir: Path, threads: int = 4):
        self.output_dir = output_dir
        self.threads = threads
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_dependencies(self):
        """检查 sra-tools 是否可用。"""
        if not shutil.which("prefetch") or not shutil.which("fasterq-dump"):
            raise RuntimeError("sra-tools (prefetch, fasterq-dump) not found in PATH.")

    def download(self, sra_ids: list[str]) -> Path:
        """
        下载 SRA 数据并转换为 FASTQ。
        返回包含下载的 FASTQ 文件的目录。
        """
        self.check_dependencies()

        logger.info(f"Starting download for {len(sra_ids)} SRA samples: {', '.join(sra_ids)}")

        for sra_id in sra_ids:
            self.process_single_sra(sra_id)

        return self.output_dir

    def process_single_sra(self, sra_id: str):
        """处理单个 SRA ID: prefetch -> fasterq-dump。"""
        # 检查文件是否已存在
        # fasterq-dump 输出格式: {sra_id}_1.fastq, {sra_id}_2.fastq (双端) 或 {sra_id}.fastq (单端)
        # 我们查找以 sra_id 开头的 .fastq 文件
        existing_files = list(self.output_dir.glob(f"{sra_id}*.fastq")) + list(self.output_dir.glob(f"{sra_id}*.fq"))

        if existing_files:
            logger.info(f"FASTQ files for {sra_id} already exist. Skipping download.")
            return

        logger.info(f"Prefetching {sra_id}...")
        try:
            # prefetch 到输出目录
            # prefetch 通常创建一个名为 sra_id 的目录或下载 .sra 文件
            # 我们使用 --output-directory 保持整洁
            # 然而，prefetch 可能会下载到缓存目录。
            # 使用 --output-directory 更安全。
            run_command(["prefetch", sra_id, "--output-directory", str(self.output_dir)], check=True)
        except Exception as e:
            logger.error(f"Prefetch failed for {sra_id}: {e}")
            raise

        logger.info(f"Converting {sra_id} to FASTQ...")
        try:
            # fasterq-dump
            # 需要找到 .sra 文件路径。prefetch 通常将其放在 output_dir/sra_id/sra_id.sra
            sra_file_dir = self.output_dir / sra_id
            sra_file = sra_file_dir / f"{sra_id}.sra"

            # 如果那里没找到，也许直接在 output_dir 中（旧版本？）
            if not sra_file.exists():
                # 直接尝试 output_dir
                sra_file = self.output_dir / f"{sra_id}.sra"

            # 如果仍然没找到，prefetch 可能静默失败了或结构不同。
            # 但我们要假设标准结构。

            # fasterq-dump 参数:
            # --split-3: 将双端拆分为 _1.fastq 和 _2.fastq
            # --outdir: 输出目录
            # --threads: 线程数
            # --progress: 显示进度

            # 注意: fasterq-dump 需要 accession ID 或路径。
            # 如果我们传递 ID，它会在缓存/当前目录中查找。
            # 既然我们 prefetch 到了特定目录，如果可能的话应该传递 .sra 文件的路径，
            # 或者确保配置允许。
            # 实际上，传递目录或文件路径效果最好。

            target = str(sra_file) if sra_file.exists() else sra_id

            run_command(
                [
                    "fasterq-dump",
                    target,
                    "--split-3",
                    "--outdir",
                    str(self.output_dir),
                    "--threads",
                    str(self.threads),
                    "--progress",
                ],
                check=True,
            )

            # 清理 .sra 文件以节省空间
            if sra_file_dir.exists() and sra_file_dir.is_dir():
                shutil.rmtree(sra_file_dir)
            elif sra_file.exists():
                sra_file.unlink()

            # 压缩 fastq 文件以节省空间并匹配 pipeline 期望 (.fastq.gz)
            # 这是可选的但很好的做法。pipeline 支持 .fastq.gz。
            # 让我们压缩它们。
            self._compress_fastq(sra_id)

        except Exception as e:
            logger.error(f"fasterq-dump failed for {sra_id}: {e}")
            raise

    def _compress_fastq(self, sra_id: str):
        """将生成的 .fastq 文件压缩为 .fastq.gz。"""
        logger.info(f"Compressing FASTQ files for {sra_id}...")
        fastqs = list(self.output_dir.glob(f"{sra_id}*.fastq"))

        for fq in fastqs:
            if shutil.which("pigz"):
                run_command(["pigz", "-p", str(self.threads), str(fq)], check=True)
            elif shutil.which("gzip"):
                run_command(["gzip", str(fq)], check=True)
            else:
                logger.warning("Neither pigz nor gzip found. Keeping files uncompressed.")
