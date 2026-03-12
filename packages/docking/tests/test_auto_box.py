from unittest.mock import MagicMock, patch

import pytest
from bio_analyze_docking.cli import get_app
from bio_analyze_docking.prep import get_box_from_receptor
from typer.testing import CliRunner

runner = CliRunner()
app = get_app()


@pytest.fixture
def test_data(tmp_path):
    # 创建模拟的 PDBQT 文件
    rec = tmp_path / "receptor.pdbqt"
    rec.write_text(
        """
ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A   1      10.000  10.000  10.000  1.00  0.00           C
"""
    )
    lig = tmp_path / "ligand.pdbqt"
    lig.write_text("ATOM      1  C   LIG A   1       1.000   1.000   1.000  1.00  0.00           C")

    output_dir = tmp_path / "output"

    return rec, lig, output_dir


def test_get_box_from_receptor(test_data):
    rec, _, _ = test_data
    center, size = get_box_from_receptor(rec, padding=0.0)

    # 坐标是 (0,0,0) 和 (10,10,10)
    # 最小 (0,0,0), 最大 (10,10,10)
    # 中心 (5,5,5)
    # 大小 (10,10,10)
    # 但是我们有 np.maximum(size, [10,10,10]) 保护
    # 让我们加点 padding 看看
    center_p, size_p = get_box_from_receptor(rec, padding=4.0)
    # 大小应该变成 14

    assert center == [5.0, 5.0, 5.0]
    assert size == [10.0, 10.0, 10.0]
    assert size_p == [14.0, 14.0, 14.0]


def test_cli_default_box(test_data):
    rec, lig, output_dir = test_data

    # Mock run_docking to avoid actual execution
    with patch("bio_analyze_docking.cli.run_docking") as mock_run:
        mock_run.return_value = {
            "best_score": -5.0,
            "output_file": str(output_dir / "docked.pdbqt"),
            "box_center": [5, 5, 5],
            "box_size": [14, 14, 14],
        }

        # 运行 CLI，不提供盒子参数
        result = runner.invoke(app, ["run", "--receptor", str(rec), "--ligand", str(lig), "--output", str(output_dir)])

        assert result.exit_code == 0
        assert "Docking box will be calculated from receptor" in result.output

        # 检查传递给 run_docking 的参数
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["center"] is None
        assert call_kwargs["size"] is None
        # run_docking 内部会处理 None，但我们这里只 mock 了 CLI 层的调用
        # run_docking 实际上会调用 run_docking_task 或者类似的逻辑
        # 在 api.py 中，run_docking 会创建 DockingNode 并运行
        # DockingNode 会调用 get_box_from_receptor


def test_docking_node_auto_box(test_data):
    rec, lig, output_dir = test_data

    from bio_analyze_docking.nodes import DockingNode

    from bio_analyze_core.pipeline import Context

    # Mock context and progress
    context = Context()
    context["rec_key"] = str(rec)
    context["lig_key"] = str(lig)
    progress = MagicMock()
    logger = MagicMock()

    node = DockingNode(
        receptor_key="rec_key",
        ligand_key="lig_key",
        output_dir=output_dir,
        center=None,  # 测试默认行为
        size=None,
        padding=4.0,
    )

    # Mock DockingEngineFactory created engine
    with patch("bio_analyze_docking.nodes.DockingEngineFactory") as mock_factory:
        mock_engine = MagicMock()
        mock_factory.create_engine.return_value = mock_engine
        mock_engine.save_results.return_value = output_dir / "docked.pdbqt"
        mock_engine.score.return_value = -7.0
        mock_engine.get_all_poses_info.return_value = []

        node.run(context, progress, logger)

        # 验证 compute_box 被调用，且参数是从受体计算出来的
        # 中心应该是 [5,5,5]，大小 [14,14,14] (padding 4.0)
        mock_engine.compute_box.assert_called_once()
        args = mock_engine.compute_box.call_args[0]
        center, size = args

        assert center == [5.0, 5.0, 5.0]
        assert size == [14.0, 14.0, 14.0]
