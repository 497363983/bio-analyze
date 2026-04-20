from __future__ import annotations

import os
from pathlib import Path

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)

GTF_PATTERNS = ("*.annotation.gtf", "*.gtf", "*.annotation.gtf.gz", "*.gtf.gz")

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
    """Genome manager."""
    def __init__(
        self,
        species: str | None,
        assembly: str | None,
        provider: str | None,
        fasta: Path | None,
        gtf: Path | None,
        output_dir: Path,
    ):
        """
        Initialize the genome manager.

        Args:
            species (str | None): Species name (e.g., "Homo sapiens").
            assembly (str | None): Reference assembly accession (e.g. "GCA_013347765.1").
            provider (str | None): Provider name (e.g. "NCBI").
            fasta (Path | None): Path to genome FASTA file.
            gtf (Path | None): Path to genome GTF file.
            output_dir (Path): Path to the output directory.
        """
        self.species = species
        self.assembly = assembly
        self.provider = provider
        self.fasta = fasta
        self.gtf = gtf
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_existing_reference(self, genome_query: str, localname: str) -> dict | None:
        """Find previously downloaded reference files before attempting a new download."""
        return discover_reference_files(self.output_dir, genome_query=genome_query, localname=localname)

    def prepare(self) -> dict:
        """
        Prepare the reference genome.

        If local files are provided, use them directly. Otherwise, try to
        download the reference with genomepy.

        Returns:
            dict: Dictionary containing `fasta` and `gtf` paths.

        Raises:
            RuntimeError: If genomepy is not installed or download fails.
            ValueError: If neither species name nor local files are provided.
        """
        if self.fasta and self.gtf:
            logger.info(f"Using provided reference files: {self.fasta}, {self.gtf}")
            return {"fasta": self.fasta, "gtf": self.gtf}

        genome_query = self.assembly or self.species

        if genome_query:
            if genomepy is None:
                raise RuntimeError("genomepy is not installed or failed to import. Cannot download genome.")

            query_label = "assembly" if self.assembly else "species"
            logger.info(f"Attempting to download reference for {query_label}: {genome_query}")
            try:
                provider_errors = []
                if self.provider:
                    providers = (self.provider,)
                elif self.assembly:
                    providers = (None,)
                else:
                    providers = ("UCSC", "NCBI", "Ensembl")
                localname = self.assembly or (self.species or genome_query).replace(" ", "_")

                existing_reference = self._find_existing_reference(genome_query, localname)
                if existing_reference:
                    logger.info(f"Reusing existing reference for {genome_query} from {self.output_dir}")
                    return existing_reference

                for provider in providers:
                    try:
                        if provider is None:
                            logger.info(f"Trying auto provider detection for assembly: {genome_query}")
                        else:
                            logger.info(f"Trying provider '{provider}' for species: {genome_query}")

                        genomepy.install_genome(
                            genome_query,
                            provider=provider,
                            annotation=True,
                            force=False,
                            genomes_dir=str(self.output_dir),
                            localname=localname,
                        )
                        provider_label = provider or "auto"
                        logger.info(f"Downloaded reference for {genome_query} from {provider_label}")
                        break
                    except Exception as provider_error:
                        provider_label = provider or "auto"
                        provider_errors.append(f"{provider_label}: {provider_error}")
                        logger.warning(f"Provider '{provider_label}' failed for {genome_query}: {provider_error}")
                else:
                    raise RuntimeError("; ".join(provider_errors))

                existing_reference = self._find_existing_reference(genome_query, localname)
                if not existing_reference:
                    raise FileNotFoundError(
                        f"Could not find FASTA file for {genome_query} in {self.output_dir}"
                    )

                return existing_reference

            except Exception as e:
                logger.error(f"Failed to download genome: {e}")
                raise RuntimeError(
                    "Genome preparation failed. Please provide local FASTA/GTF files."
                ) from e

        raise ValueError("Either species, assembly, or local FASTA/GTF files must be provided.")


def discover_reference_files(
    output_dir: Path, genome_query: str | None = None, localname: str | None = None
) -> dict | None:
    """Search the reference directory for FASTA and GTF/GTF.GZ files."""
    candidate_dirs = []
    for name in (localname, genome_query):
        if not name:
            continue
        candidate_dirs.extend(
            [
                output_dir / name,
                output_dir / name.replace(" ", "_"),
            ]
        )

    search_dirs = []
    seen = set()
    for path in candidate_dirs:
        if path.exists() and path not in seen:
            search_dirs.append(path)
            seen.add(path)

    if not search_dirs:
        search_dirs = [output_dir]

    fasta_files = []
    gtf_files = []
    for search_dir in search_dirs:
        fasta_files.extend(sorted(search_dir.rglob("*.fa")))
        fasta_files.extend(sorted(search_dir.rglob("*.fasta")))
        for pattern in GTF_PATTERNS:
            gtf_files.extend(sorted(search_dir.rglob(pattern)))

    if not fasta_files:
        return None

    return {"fasta": fasta_files[0], "gtf": gtf_files[0] if gtf_files else None}
