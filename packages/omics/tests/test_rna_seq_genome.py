from pathlib import Path
from unittest.mock import MagicMock

import pytest

from bio_analyze_omics.rna_seq.commands.utils import search_and_select_reference
from bio_analyze_omics.rna_seq.genome import GenomeManager


def test_prepare_falls_back_between_providers_and_finds_underscored_dir(tmp_path, monkeypatch):
    output_dir = tmp_path / "reference"
    species = "Scophthalmus maximus"

    install_calls = []

    def fake_install_genome(name, provider, annotation, force, genomes_dir, localname):
        install_calls.append(provider)
        if provider == "UCSC":
            raise RuntimeError("not found on UCSC")

        species_dir = Path(genomes_dir) / localname
        species_dir.mkdir(parents=True, exist_ok=True)
        (species_dir / f"{name.replace(' ', '_')}.fa").write_text(">chr1\nACGT\n", encoding="utf-8")
        (species_dir / f"{name.replace(' ', '_')}.annotation.gtf").write_text("chr1\ttest\n", encoding="utf-8")

    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.genome.genomepy",
        MagicMock(install_genome=fake_install_genome),
    )

    manager = GenomeManager(species=species, assembly=None, provider=None, fasta=None, gtf=None, output_dir=output_dir)
    ref_info = manager.prepare()

    assert install_calls == ["UCSC", "NCBI"]
    assert ref_info["fasta"] == output_dir / "Scophthalmus_maximus" / "Scophthalmus_maximus.fa"
    assert ref_info["gtf"] == output_dir / "Scophthalmus_maximus" / "Scophthalmus_maximus.annotation.gtf"


def test_prepare_uses_assembly_accession_with_auto_provider(tmp_path, monkeypatch):
    output_dir = tmp_path / "reference"
    assembly = "GCA_013347765.1"
    install_calls = []

    def fake_install_genome(name, provider, annotation, force, genomes_dir, localname):
        install_calls.append((name, provider, localname))
        species_dir = Path(genomes_dir) / localname
        species_dir.mkdir(parents=True, exist_ok=True)
        (species_dir / f"{assembly}.fa").write_text(">chr1\nACGT\n", encoding="utf-8")
        (species_dir / f"{assembly}.annotation.gtf").write_text("chr1\ttest\n", encoding="utf-8")

    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.genome.genomepy",
        MagicMock(install_genome=fake_install_genome),
    )

    manager = GenomeManager(species=None, assembly=assembly, provider=None, fasta=None, gtf=None, output_dir=output_dir)
    ref_info = manager.prepare()

    assert install_calls == [(assembly, None, assembly)]
    assert ref_info["fasta"] == output_dir / assembly / f"{assembly}.fa"
    assert ref_info["gtf"] == output_dir / assembly / f"{assembly}.annotation.gtf"


def test_prepare_uses_selected_provider_for_assembly(tmp_path, monkeypatch):
    output_dir = tmp_path / "reference"
    assembly = "GCA_009764425.1"
    install_calls = []

    def fake_install_genome(name, provider, annotation, force, genomes_dir, localname):
        install_calls.append((name, provider, localname))
        species_dir = Path(genomes_dir) / localname
        species_dir.mkdir(parents=True, exist_ok=True)
        (species_dir / f"{assembly}.fa").write_text(">chr1\nACGT\n", encoding="utf-8")

    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.genome.genomepy",
        MagicMock(install_genome=fake_install_genome),
    )

    manager = GenomeManager(
        species="Scophthalmus maximus",
        assembly=assembly,
        provider="NCBI",
        fasta=None,
        gtf=None,
        output_dir=output_dir,
    )
    ref_info = manager.prepare()

    assert install_calls == [(assembly, "NCBI", assembly)]
    assert ref_info["fasta"] == output_dir / assembly / f"{assembly}.fa"
    assert ref_info["gtf"] is None


def test_prepare_reuses_existing_downloaded_reference_without_reinstall(tmp_path, monkeypatch):
    output_dir = tmp_path / "reference"
    localname = "ASM1334776v1"
    species_dir = output_dir / localname
    species_dir.mkdir(parents=True, exist_ok=True)
    fasta = species_dir / f"{localname}.fa"
    gtf = species_dir / f"{localname}.annotation.gtf"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")
    gtf.write_text("chr1\ttest\n", encoding="utf-8")

    install_mock = MagicMock()
    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.genome.genomepy",
        MagicMock(install_genome=install_mock),
    )

    manager = GenomeManager(
        species="Scophthalmus maximus",
        assembly=localname,
        provider="Ensembl",
        fasta=None,
        gtf=None,
        output_dir=output_dir,
    )
    ref_info = manager.prepare()

    install_mock.assert_not_called()
    assert ref_info["fasta"] == fasta
    assert ref_info["gtf"] == gtf


def test_prepare_reuses_existing_gtf_gz_without_reinstall(tmp_path, monkeypatch):
    output_dir = tmp_path / "reference"
    localname = "ASM1334776v1"
    species_dir = output_dir / localname
    species_dir.mkdir(parents=True, exist_ok=True)
    fasta = species_dir / f"{localname}.fa"
    gtf_gz = species_dir / f"{localname}.annotation.gtf.gz"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")
    gtf_gz.write_text("compressed-gtf-placeholder", encoding="utf-8")

    install_mock = MagicMock()
    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.genome.genomepy",
        MagicMock(install_genome=install_mock),
    )

    manager = GenomeManager(
        species="Scophthalmus maximus",
        assembly=localname,
        provider="Ensembl",
        fasta=None,
        gtf=None,
        output_dir=output_dir,
    )
    ref_info = manager.prepare()

    install_mock.assert_not_called()
    assert ref_info["fasta"] == fasta
    assert ref_info["gtf"] == gtf_gz


def test_search_and_select_reference_returns_accession_and_provider(monkeypatch):
    results = [
        ["scMax1", "UCSC", "GCA_000000001.1", 52904, True, "Scophthalmus maximus", "Assembly 1"],
        ["ASM1334776v1", "Ensembl", "GCA_013347765.1", 52904, True, "Scophthalmus maximus", "Assembly 2"],
    ]

    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.commands.utils.genomepy",
        MagicMock(search=lambda species: results),
    )
    monkeypatch.setattr("bio_analyze_omics.rna_seq.commands.utils.prompt", lambda *args, **kwargs: 2)

    query, provider = search_and_select_reference("Scophthalmus maximus")

    assert query == "ASM1334776v1"
    assert provider == "Ensembl"


def test_search_and_select_reference_rejects_invalid_choice(monkeypatch):
    results = [["scMax1", "NCBI", "GCA_000000001.1", 52904, False, "Scophthalmus maximus", "Assembly 1"]]

    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.commands.utils.genomepy",
        MagicMock(search=lambda species: results),
    )
    monkeypatch.setattr("bio_analyze_omics.rna_seq.commands.utils.prompt", lambda *args, **kwargs: 5)

    with pytest.raises(Exception):
        search_and_select_reference("Scophthalmus maximus")


def test_search_and_select_reference_accepts_list_rows_from_genomepy(monkeypatch):
    results = [
        ["turbot", "NCBI", "GCA_009764425.1", 52904, False, "Scophthalmus maximus", "YSFRI"],
    ]

    monkeypatch.setattr(
        "bio_analyze_omics.rna_seq.commands.utils.genomepy",
        MagicMock(search=lambda species: results),
    )
    monkeypatch.setattr("bio_analyze_omics.rna_seq.commands.utils.prompt", lambda *args, **kwargs: 1)

    query, provider = search_and_select_reference("Scophthalmus maximus")

    assert query == "turbot"
    assert provider == "NCBI"
