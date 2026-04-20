from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from docstring_parser import parse as parse_docstring

sys.modules["pydeseq2"] = MagicMock()
sys.modules["pydeseq2.dds"] = MagicMock()
sys.modules["pydeseq2.ds"] = MagicMock()
sys.modules["pydeseq2.default_inference"] = MagicMock()
sys.modules["rdkit"] = MagicMock()
sys.modules["rdkit.Chem"] = MagicMock()
sys.modules["rdkit.Chem.AllChem"] = MagicMock()
sys.modules["meeko"] = MagicMock()
sys.modules["pdbfixer"] = MagicMock()
sys.modules["openmm"] = MagicMock()
sys.modules["openmm.app"] = MagicMock()
sys.modules["openmm.unit"] = MagicMock()
sys.modules["gemmi"] = MagicMock()
sys.modules["gseapy"] = MagicMock()
sys.modules["jinja2"] = MagicMock()
sys.modules["genomepy"] = MagicMock()

PACKAGES_ROOT = Path("packages")


def _load_packages() -> dict[str, dict[str, Any]]:
    from bio_analyze_core.i18n_gettext import get_translator
    from bio_analyze_core.metadata import build_cli_schema, schema_to_metadata
    from bio_analyze_docking.api import (
        run_docking,
        run_docking_batch,
        run_gnina,
        run_gnina_batch,
        run_haddock,
        run_haddock_batch,
        run_smina,
        run_smina_batch,
        run_vina,
        run_vina_batch,
    )
    from bio_analyze_docking.cli import get_app as get_docking_app
    from bio_analyze_docking.prep import prepare_ligand, prepare_receptor
    from bio_analyze_omics.cli import get_app as get_omics_app
    from bio_analyze_omics.rna_seq.commands.run import run_analysis
    from bio_analyze_plot.cli import get_app as get_plot_app
    from bio_analyze_plot.plots import (
        BarPlot,
        BoxPlot,
        ChromosomePlot,
        GSEAPlot,
        HeatmapPlot,
        LinePlot,
        PCAPlot,
        PiePlot,
        ScatterPlot,
        VolcanoPlot,
    )

    globals()["get_translator"] = get_translator
    globals()["build_cli_schema"] = build_cli_schema
    globals()["schema_to_metadata"] = schema_to_metadata

    return {
        "plot": {
            "cli_app": get_plot_app(),
            "path": PACKAGES_ROOT / "plot",
            "locale": PACKAGES_ROOT / "plot" / "locale",
            "api": {
                "volcano": VolcanoPlot.plot,
                "line": LinePlot.plot,
                "bar": BarPlot.plot,
                "box": BoxPlot.plot,
                "heatmap": HeatmapPlot.plot,
                "pca": PCAPlot.plot,
                "scatter": ScatterPlot.plot,
                "pie": PiePlot.plot,
                "chromosome": ChromosomePlot.plot,
                "gsea": GSEAPlot.plot,
            },
        },
        "docking": {
            "cli_app": get_docking_app(),
            "path": PACKAGES_ROOT / "docking",
            "locale": PACKAGES_ROOT / "docking" / "locale",
            "api": {
                "run": run_docking,
                "run_batch": run_docking_batch,
                "run_vina": run_vina,
                "run_smina": run_smina,
                "run_gnina": run_gnina,
                "run_haddock": run_haddock,
                "run_vina_batch": run_vina_batch,
                "run_smina_batch": run_smina_batch,
                "run_gnina_batch": run_gnina_batch,
                "run_haddock_batch": run_haddock_batch,
                "prepare_ligand": prepare_ligand,
                "prepare_receptor": prepare_receptor,
            },
        },
        "omics": {
            "cli_app": get_omics_app(),
            "path": PACKAGES_ROOT / "omics",
            "locale": PACKAGES_ROOT / "omics" / "locale",
            "api": {"run": run_analysis},
        },
    }


def get_param_type(param: inspect.Parameter) -> str:
    if param.annotation == inspect.Parameter.empty:
        return "any"
    annotation = str(param.annotation)
    if "Path" in annotation:
        return "path"
    if "int" in annotation:
        return "int"
    if "float" in annotation:
        return "float"
    if "bool" in annotation:
        return "bool"
    if "str" in annotation:
        return "string"
    if "list" in annotation or "List" in annotation:
        return "list"
    if "dict" in annotation or "Dict" in annotation:
        return "dict"
    if "DataFrame" in annotation:
        return "DataFrame"
    return annotation.replace("typing.", "").replace("<class '", "").replace("'>", "")


def _to_bilingual(text: str, translator: Any) -> dict[str, str]:
    normalized = text or ""
    current_language = translator.get_language()
    try:
        translator.set_language("en_US")
        en_text = translator.gettext(normalized) if normalized else ""
        if not en_text:
            en_text = normalized
        translator.set_language("zh_CN")
        zh_text = translator.gettext(normalized) if normalized else ""
        if not zh_text:
            zh_text = en_text
        return {"zh": zh_text, "en": en_text}
    finally:
        translator.set_language(current_language)


def parse_api_function(func: Any, name: str, translator: Any) -> dict[str, Any]:
    target_func = func
    sig = inspect.signature(target_func)
    doc = parse_docstring(inspect.getdoc(target_func) or "")
    doc_params = {p.arg_name: p.description or "" for p in doc.params}
    params_list = []

    for param_name, param in sig.parameters.items():
        if param_name in {"self", "cls"}:
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        required = param.default == inspect.Parameter.empty
        default_val = None if required else param.default
        params_list.append(
            {
                "name": param_name,
                "type": get_param_type(param),
                "required": required,
                "default": str(default_val) if default_val is not None else None,
                "description": _to_bilingual(doc_params.get(param_name, ""), translator),
            }
        )

    func_desc = doc.short_description or ""
    if doc.long_description:
        func_desc += f"\n{doc.long_description}"
    return {
        "name": name,
        "type": "api",
        "description": _to_bilingual(func_desc, translator),
        "params": params_list,
    }


def process_cli_app(cli_app: Any, metadata_dir: Path, translator: Any) -> None:
    from bio_analyze_core.metadata import build_cli_schema, schema_to_metadata

    schema_dir = metadata_dir / "schema"
    schema_dir.mkdir(parents=True, exist_ok=True)

    for schema_entry in build_cli_schema(cli_app):
        print(f"  - Generating CLI schema: {schema_entry['name']}")
        schema_file = schema_dir / f"{schema_entry['name']}_cli.schema.json"
        with schema_file.open("w", encoding="utf-8") as handle:
            json.dump(schema_entry, handle, indent=2, ensure_ascii=False)

        print(f"  - Generating CLI metadata: {schema_entry['name']}")
        metadata = schema_to_metadata(schema_entry, translator)
        output_file = metadata_dir / f"{schema_entry['name']}_cli.json"
        with output_file.open("w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2, ensure_ascii=False)


def main() -> None:
    from bio_analyze_core.i18n_gettext import get_translator

    packages = _load_packages()
    for pkg_name, info in packages.items():
        metadata_dir = info["path"] / "metadata"
        metadata_dir.mkdir(exist_ok=True)

        translator = get_translator(str(info["locale"].resolve()))
        translator.set_language("en_US")

        print(f"Processing package: {pkg_name}")
        process_cli_app(info["cli_app"], metadata_dir, translator)

        for api_name, func_or_class in info.get("api", {}).items():
            print(f"  - Generating API metadata: {api_name}")
            metadata = parse_api_function(func_or_class, api_name, translator)
            output_file = metadata_dir / f"{api_name}_api.json"
            with output_file.open("w", encoding="utf-8") as handle:
                json.dump(metadata, handle, indent=2, ensure_ascii=False)

    print("Done!")


if __name__ == "__main__":
    main()
