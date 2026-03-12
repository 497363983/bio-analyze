from unittest.mock import MagicMock

import pandas as pd
from bio_analyze_docking.nodes import ResultSummaryNode

from bio_analyze_core.pipeline import Context


def test_result_summary_node_csv(tmp_path):
    output_path = tmp_path / "summary.csv"
    node = ResultSummaryNode(input_key="results", output_path=output_path, format="csv")

    # Context requires a string path, not a Path object
    # In recent versions of bio_analyze_core, Context might expect a string or Path.
    # If tmp_path is a PosixPath (in docker), and Context iterates over it, it means Context.__init__ is treating it as iterable instead of path?
    # Let's check Context implementation or just pass str(tmp_path) and ensure it works.
    # The previous error "TypeError: 'PosixPath' object is not iterable" suggests Context might be doing something like:
    # self.data = dict(initial_data) where initial_data is the argument.
    # If Context(path) is the signature, maybe it's Context(storage_path=...) or similar?
    # Let's check bio_analyze_core/pipeline.py if possible, but for now let's assume Context takes a dict as first arg or kwargs?
    # Ah, if Context(tmp_path) fails, maybe the first arg is NOT the path.
    # Let's try Context(storage_dir=tmp_path) or just Context() if storage is optional.

    context = Context(storage_dir=tmp_path)
    context["results"] = [
        {
            "receptor": "rec1",
            "ligand": "lig1",
            "status": "success",
            "poses": [{"affinity": -9.5, "rmsd_lb": 0.0, "rmsd_ub": 0.0}],
            "output_file": "/path/to/out1",
        },
        {"receptor": "rec2", "ligand": "lig2", "status": "failed", "error": "Some error"},
    ]

    node.run(context, MagicMock(), MagicMock())

    assert output_path.exists()
    df = pd.read_csv(output_path)
    assert len(df) == 2
    assert df.iloc[0]["Receptor"] == "rec1"
    assert df.iloc[0]["Affinity (kcal/mol)"] == -9.5
    assert df.iloc[1]["Status"] == "failed"


def test_result_summary_node_excel(tmp_path):
    output_path = tmp_path / "summary.xlsx"
    node = ResultSummaryNode(input_key="results", output_path=output_path, format="excel")

    context = Context(storage_dir=tmp_path)
    context["results"] = [
        {
            "receptor": "rec1",
            "ligand": "lig1",
            "status": "success",
            "poses": [{"affinity": -8.0}],
            "output_file": "/path/to/out1",
        }
    ]

    node.run(context, MagicMock(), MagicMock())

    assert output_path.exists()
    df = pd.read_excel(output_path)
    assert len(df) == 1
    assert df.iloc[0]["Affinity (kcal/mol)"] == -8.0
