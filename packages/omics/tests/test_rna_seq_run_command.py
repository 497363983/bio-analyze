"""Tests for the RNA-Seq run command."""

import json
from unittest.mock import patch

from bio_analyze_omics.rna_seq.commands.run import run_analysis


def _base_kwargs(tmp_path, output_dir, design_file):
    return {
        "config_file": None,
        "input_dir": tmp_path / "input",
        "sra_ids": None,
        "output_dir": output_dir,
        "design_file": design_file,
        "species": "Scophthalmus maximus",
        "assembly": None,
        "genome_fasta": None,
        "genome_gtf": None,
        "threads": 4,
        "skip_qc": False,
        "skip_trim": False,
        "star_align": False,
        "quant_tool": "salmon",
        "quant_compare_tools": [],
        "theme": "default",
        "step": None,
        "qualified_quality_phred": None,
        "unqualified_percent_limit": None,
        "n_base_limit": None,
        "length_required": None,
        "max_len1": None,
        "max_len2": None,
        "adapter_sequence": None,
        "adapter_sequence_r2": None,
        "trim_front1": None,
        "trim_tail1": None,
        "cut_right": False,
        "cut_window_size": None,
        "cut_mean_quality": None,
        "dedup": False,
        "poly_g_min_len": None,
    }


@patch("bio_analyze_omics.rna_seq.commands.run.RNASeqPipeline")
@patch("bio_analyze_omics.rna_seq.commands.run.search_and_select_reference")
def test_run_analysis_reuses_saved_reference_selection(mock_search, mock_pipeline_cls, tmp_path):
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    design_file = tmp_path / "design.csv"
    design_file.write_text("sample,condition\n", encoding="utf-8")
    state = {
        "context": {
            "species": "Scophthalmus maximus",
            "assembly": "ASM1334776v1",
            "provider": "Ensembl",
        }
    }
    with open(output_dir / "pipeline_state.json", "w", encoding="utf-8") as handle:
        json.dump(state, handle)

    pipeline = mock_pipeline_cls.return_value
    run_analysis(**_base_kwargs(tmp_path, output_dir, design_file))

    mock_search.assert_not_called()
    mock_pipeline_cls.assert_called_once()
    assert mock_pipeline_cls.call_args.kwargs["assembly"] == "ASM1334776v1"
    assert mock_pipeline_cls.call_args.kwargs["provider"] == "Ensembl"
    pipeline.run.assert_called_once()


@patch("bio_analyze_omics.rna_seq.commands.run.RNASeqPipeline")
@patch(
    "bio_analyze_omics.rna_seq.commands.run.search_and_select_reference",
    return_value=("ASM1334776v1", "Ensembl"),
)
def test_run_analysis_prompts_when_state_lacks_selection(mock_search, mock_pipeline_cls, tmp_path):
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    design_file = tmp_path / "design.csv"
    design_file.write_text("sample,condition\n", encoding="utf-8")

    pipeline = mock_pipeline_cls.return_value
    run_analysis(**_base_kwargs(tmp_path, output_dir, design_file))

    mock_search.assert_called_once_with("Scophthalmus maximus")
    assert mock_pipeline_cls.call_args.kwargs["assembly"] == "ASM1334776v1"
    assert mock_pipeline_cls.call_args.kwargs["provider"] == "Ensembl"
    pipeline.run.assert_called_once()


@patch("bio_analyze_omics.rna_seq.commands.run.search_and_select_reference")
@patch("bio_analyze_omics.rna_seq.commands.run.load_config")
@patch("bio_analyze_omics.rna_seq.commands.run.RNASeqPipeline")
def test_run_analysis_loads_quant_config_from_config_file(
    mock_pipeline_cls,
    mock_load_config,
    mock_search,
    tmp_path,
):
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    design_file = tmp_path / "design.csv"
    design_file.write_text("sample,condition\n", encoding="utf-8")
    config_file = tmp_path / "config.yaml"
    config_file.write_text("quant: {}\n", encoding="utf-8")
    mock_load_config.return_value = {
        "input_dir": str(tmp_path / "input"),
        "output_dir": str(output_dir),
        "design_file": str(design_file),
        "quant": {
            "tool": "salmon",
            "compare_tools": ["kallisto", "featurecounts"],
            "primary": {"template": "default", "sample_workers": 2},
            "compare": {"kallisto": {"template": "bootstrap"}},
        },
    }

    kwargs = _base_kwargs(tmp_path, output_dir, design_file)
    kwargs["config_file"] = config_file
    kwargs["species"] = None
    run_analysis(**kwargs)

    mock_search.assert_not_called()
    pipeline_kwargs = mock_pipeline_cls.call_args.kwargs
    assert pipeline_kwargs["quant_tool"] == "salmon"
    assert pipeline_kwargs["quant_compare_tools"] == ["kallisto", "featurecounts"]
    assert pipeline_kwargs["quant_config"] == {
        "primary": {"template": "default", "sample_workers": 2},
        "compare": {"kallisto": {"template": "bootstrap"}},
    }


@patch("bio_analyze_omics.rna_seq.commands.run.RNASeqPipeline")
@patch("bio_analyze_omics.rna_seq.commands.run.search_and_select_reference")
def test_run_analysis_restores_quant_settings_from_state(mock_search, mock_pipeline_cls, tmp_path):
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    design_file = tmp_path / "design.csv"
    design_file.write_text("sample,condition\n", encoding="utf-8")
    state = {
        "context": {
            "species": "Scophthalmus maximus",
            "assembly": "ASM1334776v1",
            "provider": "Ensembl",
            "quant_tool": "kallisto",
            "quant_compare_tools": ["featurecounts"],
            "quant_config": {
                "primary": {"template": "bootstrap"},
                "compare": {"featurecounts": {"template": "fractional"}},
            },
        }
    }
    with open(output_dir / "pipeline_state.json", "w", encoding="utf-8") as handle:
        json.dump(state, handle)

    kwargs = _base_kwargs(tmp_path, output_dir, design_file)
    kwargs["quant_tool"] = None
    kwargs["quant_compare_tools"] = []
    run_analysis(**kwargs)

    mock_search.assert_not_called()
    pipeline_kwargs = mock_pipeline_cls.call_args.kwargs
    assert pipeline_kwargs["quant_tool"] == "kallisto"
    assert pipeline_kwargs["quant_compare_tools"] == ["featurecounts"]
    assert pipeline_kwargs["quant_config"] == {
        "primary": {"template": "bootstrap"},
        "compare": {"featurecounts": {"template": "fractional"}},
    }
