import os
from pathlib import Path

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)

# 设置 genomepy 缓存目录为本地目录以避免权限问题
cache_dir = Path.cwd() / ".genomepy_cache"
cache_dir.mkdir(exist_ok=True)
os.environ["GENOMEPY_CACHE_DIR"] = str(cache_dir)

try:
    import genomepy
except Exception as e:
    logger.warning(f"Failed to import genomepy: {e}. Auto-download features will be disabled.")
    genomepy = None


class GenomeManager:
    def __init__(self, species: str | None, fasta: Path | None, gtf: Path | None, output_dir: Path):
        self.species = species
        self.fasta = fasta
        self.gtf = gtf
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def prepare(self) -> dict:
        """
        准备参考基因组。
        返回包含 'fasta' 和 'gtf' 路径的字典。
        """
        if self.fasta and self.gtf:
            logger.info(f"Using provided reference files: {self.fasta}, {self.gtf}")
            return {"fasta": self.fasta, "gtf": self.gtf}

        if self.species:
            if genomepy is None:
                raise RuntimeError("genomepy is not installed or failed to import. Cannot download genome.")

            logger.info(f"Attempting to download reference for species: {self.species}")
            try:
                # 使用 genomepy 安装
                # 注意：这可能需要时间和带宽
                genomepy.install_genome(
                    self.species,
                    "UCSC",
                    annotation=True,
                    force=False,
                    genome_dir=str(self.output_dir),
                )

                # 查找文件
                genome_path = self.output_dir / self.species
                fasta_files = list(genome_path.glob("*.fa")) + list(genome_path.glob("*.fasta"))
                gtf_files = list(genome_path.glob("*.gtf")) + list(genome_path.glob("*.annotation.gtf"))

                if not fasta_files:
                    raise FileNotFoundError(f"Could not find FASTA file for {self.species} in {genome_path}")

                return {"fasta": fasta_files[0], "gtf": gtf_files[0] if gtf_files else None}

            except Exception as e:
                logger.error(f"Failed to download genome: {e}")
                raise RuntimeError("Genome preparation failed. Please provide local FASTA/GTF files.")

        raise ValueError("Either species name or local FASTA/GTF files must be provided.")
