import inspect
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

# Mock localize_app BEFORE importing CLIs to ensure we get raw bilingual strings
# We create a dummy module for bio_analyze_core.cli_i18n
cli_i18n_mock = MagicMock()
cli_i18n_mock.localize_app = lambda app, lang: None  # No-op
cli_i18n_mock.detect_language = lambda: "en"  # Dummy return
sys.modules["bio_analyze_core.cli_i18n"] = cli_i18n_mock

# Mock heavy dependencies
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

# Import API functions/classes for docking (examples)
from bio_analyze_docking.api import (  # noqa: E402
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
from bio_analyze_docking.cli import get_app as get_docking_app  # noqa: E402
from bio_analyze_docking.prep import prepare_ligand, prepare_receptor  # noqa: E402

# We assume this script is run from project root, so pythonpath needs to be set
from bio_analyze_plot.cli import get_app as get_plot_app  # noqa: E402

# Import API classes for plot
from bio_analyze_plot.plots import (  # noqa: E402
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
from docstring_parser import parse as parse_docstring  # noqa: E402

# Import core i18n
from bio_analyze_core.i18n import extract_i18n_desc  # noqa: E402
from bio_analyze_rna_seq.cli import get_app as get_rna_app  # noqa: E402

# Import API for RNA-seq (examples)
from bio_analyze_rna_seq.pipeline import RNASeqPipeline  # noqa: E402

# Define package paths and registries
PACKAGES_ROOT = Path("packages")
PACKAGES = {
    "plot": {
        "cli_app": get_plot_app(),
        "path": PACKAGES_ROOT / "plot",
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
    "rna_seq": {"cli_app": get_rna_app(), "path": PACKAGES_ROOT / "rna_seq", "api": {"run": RNASeqPipeline.run}},
    "docking": {
        "cli_app": get_docking_app(),
        "path": PACKAGES_ROOT / "docking",
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
}


def get_param_type(param: inspect.Parameter) -> str:
    """Extract type name from annotation."""
    if param.annotation == inspect.Parameter.empty:
        return "any"

    # Handle Optional[type] or type | None
    annotation = str(param.annotation)
    # Simple cleanup for common types
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


def parse_cli_command(command_info: Any, cmd_name: str) -> dict[str, Any]:
    """Parse a Typer command to extract metadata."""
    callback = command_info.callback
    if not callback:
        return {"name": cmd_name, "type": "cli", "params": []}

    sig = inspect.signature(callback)
    params_list = []

    for name, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        default = param.default
        help_text = ""
        param_opts = []

        if hasattr(default, "help"):
            help_text = default.help or ""
        if hasattr(default, "param_decls"):
            param_opts = default.param_decls

        real_default = default
        if hasattr(default, "default"):
            real_default = default.default
            if real_default == ...:
                real_default = None

        if real_default == inspect.Parameter.empty:
            real_default = None

        if param_opts:
            display_name = ", ".join(param_opts)
        else:
            cli_name = name.replace("_", "-")
            display_name = f"--{cli_name}"

        type_str = get_param_type(param)
        required = (default == inspect.Parameter.empty) or (hasattr(default, "default") and default.default == ...)

        param_entry = {
            "name": display_name,
            "type": type_str,
            "required": required,
            "default": str(real_default) if real_default is not None else None,
            "description": extract_i18n_desc(help_text),
        }
        params_list.append(param_entry)

    cmd_desc = command_info.help or ""
    return {"name": cmd_name, "type": "cli", "description": extract_i18n_desc(cmd_desc), "params": params_list}


def parse_api_function(func: Any, name: str) -> dict[str, Any]:
    """Parse a Python function or method docstring to extract metadata."""

    target_func = func
    doc_str_override = ""

    # Try to find class from __qualname__
    qualname = getattr(func, "__qualname__", "")
    if "." in qualname:
        cls_name = qualname.split(".")[0]

        # Hack: for RNASeqPipeline.run, we want RNASeqPipeline.__init__
        if cls_name == "RNASeqPipeline" and name == "run":
            from bio_analyze_rna_seq.pipeline import RNASeqPipeline

            target_func = RNASeqPipeline.__init__
            # Use the class docstring instead of init docstring for parameter descriptions
            doc_str_override = inspect.getdoc(RNASeqPipeline) or ""
        elif "Plot" in cls_name and name == "plot":
            pass

    sig = inspect.signature(target_func)
    doc_str = doc_str_override or (inspect.getdoc(target_func) or "")

    doc = parse_docstring(doc_str)

    # Map docstring params
    doc_params = {p.arg_name: p.description for p in doc.params}

    params_list = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        default = param.default
        required = default == inspect.Parameter.empty
        default_val = None if required else default

        desc = doc_params.get(param_name, "")

        param_entry = {
            "name": param_name,
            "type": get_param_type(param),
            "required": required,
            "default": str(default_val) if default_val is not None else None,
            "description": extract_i18n_desc(desc),
        }
        params_list.append(param_entry)

    func_desc = doc.short_description or ""
    if doc.long_description:
        func_desc += "\n" + doc.long_description

    return {"name": name, "type": "api", "description": extract_i18n_desc(func_desc), "params": params_list}


def process_cli_app(cli_app: Any, metadata_dir: Path, prefix: str = ""):
    if not cli_app:
        return

    # Process direct commands
    for cmd_info in cli_app.registered_commands:
        cmd_name = cmd_info.name or cmd_info.callback.__name__.strip("_")
        if not cmd_name:
            continue

        full_cmd_name = f"{prefix}{cmd_name}"
        print(f"  - Generating CLI metadata: {full_cmd_name}")
        metadata = parse_cli_command(cmd_info, full_cmd_name)

        output_file = metadata_dir / f"{full_cmd_name}_cli.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Process sub-groups
    for group_info in getattr(cli_app, "registered_groups", []):
        group_name = group_info.name
        if group_info.typer_instance:
            new_prefix = f"{prefix}{group_name}_" if group_name else prefix
            process_cli_app(group_info.typer_instance, metadata_dir, new_prefix)


def main():
    for pkg_name, info in PACKAGES.items():
        cli_app = info["cli_app"]
        pkg_path = info["path"]
        api_registry = info.get("api", {})

        metadata_dir = pkg_path / "metadata"
        metadata_dir.mkdir(exist_ok=True)

        print(f"Processing package: {pkg_name}")

        # 1. Parse CLI Commands
        process_cli_app(cli_app, metadata_dir)

        # 2. Parse API Functions/Classes
        for api_name, func_or_class in api_registry.items():
            print(f"  - Generating API metadata: {api_name}")
            metadata = parse_api_function(func_or_class, api_name)

            output_file = metadata_dir / f"{api_name}_api.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("Done!")


if __name__ == "__main__":
    main()
