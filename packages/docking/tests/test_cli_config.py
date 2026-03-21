import json
from unittest.mock import patch

import pytest
import yaml
from bio_analyze_docking.cli import get_app
from typer.testing import CliRunner

runner = CliRunner()
app = get_app()


@pytest.fixture
def test_data(tmp_path):
    # 创建模拟的 PDBQT 文件
    rec = tmp_path / "receptor.pdbqt"
    rec.write_text("ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N")
    lig = tmp_path / "ligand.pdbqt"
    lig.write_text("ATOM      1  C   LIG A   1       1.000   1.000   1.000  1.00  0.00           C")

    output_dir = tmp_path / "output"

    return rec, lig, output_dir


def test_json_config(test_data, tmp_path):
    rec, lig, output_dir = test_data
    config_file = tmp_path / "config.json"

    config = {
        "receptor": str(rec),
        "ligand": str(lig),
        "output_dir": str(output_dir),
        "center_x": 0.0,
        "center_y": 0.0,
        "center_z": 0.0,
        "size_x": 15.0,
        "size_y": 15.0,
        "size_z": 15.0,
        "exhaustiveness": 1,
        "n_poses": 1,
    }

    with open(config_file, "w") as f:
        json.dump(config, f)

    # 我们这里只能测试 CLI 参数解析逻辑，无法完整运行 run_docking 因为没有安装 vina
    # 但我们可以通过捕获特定的输出来验证参数是否被正确传递
    # 由于 run_docking 会被调用并可能失败，我们需要 mock 它或者只测试 CLI 部分
    # 这里我们通过检查 typer 的输出，如果它尝试运行 run_docking，说明参数解析成功
    # 或者我们可以让参数不完整，看是否报错

    # 更好的方式：mock run_docking
    from unittest.mock import patch

    with patch("bio_analyze_docking.commands.utils.run_docking") as mock_run:
        mock_run.return_value = {
            "best_score": -7.5,
            "output_file": str(output_dir / "docked.pdbqt"),
            "box_center": [0, 0, 0],
            "box_size": [15, 15, 15],
        }

        result = runner.invoke(app, ["run", "vina", "--config", str(config_file)])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs

        assert str(call_kwargs["receptor"]) == str(rec)
        assert call_kwargs["size"][0] == 15.0
        assert call_kwargs["exhaustiveness"] == 1


def test_yaml_config(test_data, tmp_path):
    rec, lig, output_dir = test_data
    config_file = tmp_path / "config.yaml"

    config = {
        "receptor": str(rec),
        "ligand": str(lig),
        "output_dir": str(output_dir),
        "center_x": 5.0,
        "center_y": 5.0,
        "center_z": 5.0,
        "exhaustiveness": 2,
    }

    with open(config_file, "w") as f:
        yaml.dump(config, f)

    with patch("bio_analyze_docking.commands.utils.run_docking") as mock_run:
        mock_run.return_value = {
            "best_score": -6.0,
            "output_file": str(output_dir / "docked.pdbqt"),
            "box_center": [5, 5, 5],
            "box_size": [20, 20, 20],
        }

        # 命令行参数覆盖配置文件
        result = runner.invoke(app, ["run", "vina", "--config", str(config_file), "--exhaustiveness", "4"])

        assert result.exit_code == 0
        call_kwargs = mock_run.call_args.kwargs

        assert call_kwargs["center"] == [5.0, 5.0, 5.0]
        assert call_kwargs["exhaustiveness"] == 4  # 命令行覆盖


def test_missing_config_file(tmp_path):
    config_file = tmp_path / "non_existent.json"
    result = runner.invoke(app, ["run", "vina", "--config", str(config_file)])
    assert result.exit_code == 1
    # typer 可能会捕获 stderr
    # 我们在 CLI 中使用 typer.echo(..., err=True)
    # result.stdout 包含标准输出和标准错误（默认情况）
    # 但有时需要显式检查
    assert "Error loading config" in result.output


def test_invalid_config_format(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.touch()
    result = runner.invoke(app, ["run", "vina", "--config", str(config_file)])
    assert result.exit_code == 1
    assert "Error loading config" in result.output


def test_engine_config(test_data, tmp_path):
    rec, lig, output_dir = test_data

    with patch("bio_analyze_docking.commands.utils.run_docking") as mock_run:
        mock_run.return_value = {
            "best_score": -7.5,
            "output_file": str(output_dir / "docked.pdbqt"),
            "box_center": [0, 0, 0],
            "box_size": [15, 15, 15],
        }

        # Test command line argument
        result = runner.invoke(
            app,
            [
                "run",
                "gnina",
                "--receptor",
                str(rec),
                "--ligand",
                str(lig),
                "--output",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["engine"] == "gnina"

        # Test config file
        config_file = tmp_path / "config_engine.json"
        config = {
            "receptor": str(rec),
            "ligand": str(lig),
            "output_dir": str(output_dir),
            "engine": "smina",
        }
        with open(config_file, "w") as f:
            json.dump(config, f)

        result = runner.invoke(app, ["run", "smina", "--config", str(config_file)])
        assert result.exit_code == 0
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["engine"] == "smina"


def test_boxes_config_single(test_data, tmp_path):
    rec, lig, output_dir = test_data
    config_file = tmp_path / "config_boxes.json"

    config = {
        "receptor": str(rec),
        "ligand": str(lig),
        "output_dir": str(output_dir),
        "center_x": 0.0,
        "center_y": 0.0,
        "center_z": 0.0,
        "size_x": 10.0,
        "size_y": 10.0,
        "size_z": 10.0,
        "boxes": {
            rec.name: {
                "center_x": 5.0,
                "center_y": 5.0,
                "center_z": 5.0,
                "size_x": 15.0,
                "size_y": 15.0,
                "size_z": 15.0,
            }
        },
    }

    with open(config_file, "w") as f:
        json.dump(config, f)

    with patch("bio_analyze_docking.commands.utils.run_docking") as mock_run:
        mock_run.return_value = {
            "best_score": -7.5,
            "output_file": str(output_dir / "docked.pdbqt"),
            "box_center": [5, 5, 5],
            "box_size": [15, 15, 15],
        }

        result = runner.invoke(app, ["run", "vina", "--config", str(config_file)])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs

        assert call_kwargs["center"] == [5.0, 5.0, 5.0]
        assert call_kwargs["size"] == [15.0, 15.0, 15.0]


def test_boxes_config_batch(test_data, tmp_path):
    rec, lig, output_dir = test_data

    # Create directories for batch
    rec_dir = tmp_path / "receptors"
    rec_dir.mkdir()
    lig_dir = tmp_path / "ligands"
    lig_dir.mkdir()

    rec1 = rec_dir / "rec1.pdbqt"
    rec1.write_text("ATOM")
    rec2 = rec_dir / "rec2.pdbqt"
    rec2.write_text("ATOM")

    lig1 = lig_dir / "lig1.pdbqt"
    lig1.write_text("ATOM")

    config_file = tmp_path / "config_boxes_batch.json"

    boxes_dict = {
        "rec1.pdbqt": {
            "center_x": 1.0,
            "center_y": 2.0,
            "center_z": 3.0,
            "size_x": 10.0,
            "size_y": 10.0,
            "size_z": 10.0,
        },
        "rec2": {
            "center_x": 4.0,
            "center_y": 5.0,
            "center_z": 6.0,
            "size_x": 20.0,
            "size_y": 20.0,
            "size_z": 20.0,
        },
    }

    config = {"receptor": str(rec_dir), "ligand": str(lig_dir), "output_dir": str(output_dir), "boxes": boxes_dict}

    with open(config_file, "w") as f:
        json.dump(config, f)

    with patch("bio_analyze_docking.commands.utils.run_docking_batch") as mock_run_batch:
        mock_run_batch.return_value = []

        result = runner.invoke(app, ["run", "vina", "--config", str(config_file)])

        assert result.exit_code == 0
        mock_run_batch.assert_called_once()
        call_kwargs = mock_run_batch.call_args.kwargs

        assert call_kwargs["boxes"] == boxes_dict
