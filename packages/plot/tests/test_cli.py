import matplotlib
import pandas as pd
from bio_analyze_plot.cli import get_app
from typer.testing import CliRunner

matplotlib.use("Agg")

runner = CliRunner()
app = get_app()


def test_volcano_cli_csv(tmp_path):
    # Create a dummy CSV
    csv_file = tmp_path / "test.csv"
    data = pd.DataFrame({"log2FoldChange": [2.5, -3.0], "pvalue": [0.001, 0.0001]})
    data.to_csv(csv_file, index=False)

    output_file = tmp_path / "volcano.png"

    result = runner.invoke(app, ["volcano", str(csv_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_volcano_cli_excel(tmp_path):
    # Create a dummy Excel
    excel_file = tmp_path / "test.xlsx"
    data = pd.DataFrame({"log2FoldChange": [2.5, -3.0], "pvalue": [0.001, 0.0001]})
    data.to_excel(excel_file, index=False)

    output_file = tmp_path / "volcano_excel.png"

    result = runner.invoke(app, ["volcano", str(excel_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_volcano_cli_tsv(tmp_path):
    # Create a dummy TSV
    tsv_file = tmp_path / "test.tsv"
    data = pd.DataFrame({"log2FoldChange": [2.5, -3.0], "pvalue": [0.001, 0.0001]})
    data.to_csv(tsv_file, sep="\t", index=False)

    output_file = tmp_path / "volcano_tsv.png"

    result = runner.invoke(app, ["volcano", str(tsv_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_pie_cli(tmp_path):
    # Create a dummy CSV
    csv_file = tmp_path / "test_pie.csv"
    data = pd.DataFrame({"Category": ["A", "B", "C"], "Value": [10, 20, 30]})
    data.to_csv(csv_file, index=False)

    output_file = tmp_path / "pie.png"

    # Run the pie command
    result = runner.invoke(
        app,
        [
            "pie",
            str(csv_file),
            "--x",
            "Category",
            "--y",
            "Value",
            "--output",
            str(output_file),
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()


def test_box_cli(tmp_path):
    # Create a dummy CSV
    csv_file = tmp_path / "test_box.csv"
    data = pd.DataFrame(
        {"Group": ["A"] * 10 + ["B"] * 10, "Value": [10 + i for i in range(10)] + [20 + i for i in range(10)]}
    )
    data.to_csv(csv_file, index=False)

    output_file = tmp_path / "box.png"

    # Run the box command
    result = runner.invoke(
        app,
        [
            "box",
            str(csv_file),
            "--x",
            "Group",
            "--y",
            "Value",
            "--output",
            str(output_file),
            "--add-swarm",
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()
