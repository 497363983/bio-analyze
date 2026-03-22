from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from bio_analyze_cli.commands.create import TEMPLATES, ThemeTemplate, ToolTemplate, create_command


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path / "output"


def test_tool_template_create(tmp_output):
    """测试 ToolTemplate 创建工具包"""
    tmp_output.mkdir()
    template = ToolTemplate()
    name = "test_tool"

    # 执行创建
    template.create(name, tmp_output)

    # 验证生成的目录和文件
    package_dir = tmp_output / "packages" / name
    assert package_dir.exists()
    assert (package_dir / "src" / f"bio_analyze_{name}" / "__init__.py").exists()
    assert (package_dir / "tests").exists()


def test_tool_template_create_exists(tmp_output):
    """测试 ToolTemplate 目录已存在时抛出异常"""
    tmp_output.mkdir()
    template = ToolTemplate()
    name = "test_tool"

    # 提前创建目录
    package_dir = tmp_output / "packages" / name
    package_dir.mkdir(parents=True)

    with pytest.raises(typer.Exit) as exc_info:
        template.create(name, tmp_output)

    assert exc_info.value.exit_code == 1


def test_theme_template_create(tmp_output):
    """测试 ThemeTemplate 创建主题包"""
    tmp_output.mkdir()
    template = ThemeTemplate()
    name = "test-theme"

    # 执行创建
    template.create(name, tmp_output)

    # 验证生成的目录和文件
    package_dir = tmp_output / name
    assert package_dir.exists()

    # 验证连字符替换为下划线
    assert (package_dir / "src" / "test_theme" / "__init__.py").exists()


def test_theme_template_create_exists(tmp_output):
    """测试 ThemeTemplate 目录已存在时抛出异常"""
    tmp_output.mkdir()
    template = ThemeTemplate()
    name = "test-theme"

    # 提前创建目录
    package_dir = tmp_output / name
    package_dir.mkdir(parents=True)

    with pytest.raises(typer.Exit) as exc_info:
        template.create(name, tmp_output)

    assert exc_info.value.exit_code == 1


def test_create_command_with_args(tmp_output):
    """测试带参数调用 create_command"""
    tmp_output.mkdir()

    with patch.object(TEMPLATES["tool"], "create") as mock_create:
        create_command(template_type="tool", name="my_tool", output=tmp_output)
        mock_create.assert_called_once_with("my_tool", tmp_output)


def test_create_command_interactive(tmp_output):
    """测试无参数时交互式调用 create_command"""
    tmp_output.mkdir()

    with (
        patch("bio_analyze_cli.commands.create.Prompt.ask") as mock_ask,
        patch.object(TEMPLATES["theme"], "create") as mock_create,
    ):
        # 模拟连续输入 theme 和 my_theme
        mock_ask.side_effect = ["theme", "my_theme"]

        create_command(template_type=None, name=None, output=tmp_output)

        assert mock_ask.call_count == 2
        mock_create.assert_called_once_with("my_theme", tmp_output)


def test_create_command_invalid_type():
    """测试提供未知模板类型"""
    with pytest.raises(typer.Exit) as exc_info:
        create_command(template_type="invalid_type", name="my_tool", output=Path.cwd())

    assert exc_info.value.exit_code == 1
