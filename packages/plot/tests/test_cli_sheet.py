import matplotlib
import pandas as pd
from bio_analyze_plot.cli import get_app
from bio_analyze_core.cli.app import CliRunner

matplotlib.use("Agg")

runner = CliRunner()
app = get_app()


def test_cli_excel_sheet(tmp_path):
    # Create an Excel file with two sheets
    df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df2 = pd.DataFrame({"a": [5, 6], "b": [7, 8]})

    excel_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        df1.to_excel(writer, sheet_name="Sheet1", index=False)
        df2.to_excel(writer, sheet_name="Sheet2", index=False)

    # Test reading specific sheet for line plot
    output_path = tmp_path / "plot.png"
    result = runner.invoke(
        app, ["line", str(excel_path), "-o", str(output_path), "--x", "a", "--y", "b", "--sheet", "Sheet2"]
    )

    if result.exit_code != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        if result.exception:
            print("EXCEPTION:", result.exception)
            import traceback

            traceback.print_tb(result.exception.__traceback__)

    assert result.exit_code == 0
    assert "Saved line plot" in result.stdout
    assert output_path.exists()

    # Test failure with non-existent sheet
    result_fail = runner.invoke(
        app, ["line", str(excel_path), "-o", str(output_path), "--x", "a", "--y", "b", "--sheet", "NonExistent"]
    )
    assert result_fail.exit_code != 0
