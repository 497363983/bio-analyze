import importlib
import typing
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from bio_analyze_cli.main import app, create_app
from bio_analyze_cli.main import main as main_func
from bio_analyze_cli.plugins import CliPlugin

runner = CliRunner()
main_module = importlib.import_module("bio_analyze_cli.main")


def test_create_app():
    """测试创建应用实例"""
    new_app = create_app()

    # 应该包含注册的命令
    registered_commands = [cmd.name for cmd in new_app.registered_commands]
    assert "plugins" in registered_commands
    assert "create" in registered_commands


def test_root_callback_config_annotation_compatible():
    """测试 root 回调注解可被类型系统正确解析（兼容 Python 3.9）。"""
    callback = create_app().registered_callback.callback
    hints = typing.get_type_hints(callback)
    assert hints["config"] == typing.Optional[Path]



@patch.object(main_module, "load_settings")
@patch.object(main_module, "setup_logging")
def test_root_callback(mock_setup_logging, mock_load_settings):
    """测试根回调命令和配置加载"""
    mock_settings = MagicMock()
    mock_settings.log_level = "DEBUG"
    mock_load_settings.return_value = mock_settings

    # 使用 --config 参数调用任意存在的不执行实际操作的命令（例如 plugins，并 mock 它）
    # 但最简单的是仅调用帮助，看是否触发 root 回调？
    # 不，help 不会触发 root callback，我们需要调用一个子命令

    with patch.object(main_module, "load_plugins") as mock_load_plugins:
        mock_load_plugins.return_value = []
        result = runner.invoke(app, ["--config", "test.toml", "plugins"])

        assert result.exit_code == 0
        mock_load_settings.assert_called_once()
        mock_setup_logging.assert_called_once_with("DEBUG")


@patch.object(main_module, "load_plugins")
def test_plugins_command(mock_load_plugins):
    """测试 plugins 子命令"""
    mock_plugin1 = MagicMock(spec=CliPlugin)
    mock_plugin1.name = "plugin_a"
    mock_plugin2 = MagicMock(spec=CliPlugin)
    mock_plugin2.name = "plugin_b"

    mock_load_plugins.return_value = [mock_plugin1, mock_plugin2]

    # 调用 plugins 命令
    result = runner.invoke(app, ["plugins"])

    assert result.exit_code == 0
    assert "plugin_a" in result.stdout
    assert "plugin_b" in result.stdout


@patch.object(main_module, "app")
@patch.object(main_module, "localize_app")
@patch.object(main_module, "detect_language")
def test_main_function(mock_detect_language, mock_localize_app, mock_app):
    """测试主入口函数"""
    mock_detect_language.return_value = "zh"

    # 执行主函数
    main_func()

    # 验证国际化和应用启动调用
    mock_detect_language.assert_called_once()
    mock_localize_app.assert_called_once_with(mock_app, "zh")
    mock_app.assert_called_once()
