import importlib
from unittest.mock import MagicMock, patch

from bio_analyze_core.cli.app import CliRunner

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
        result = runner.invoke(app, ["plugins"])

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
    rendered = result.stdout + result.stderr
    assert "plugin_a" in rendered
    assert "plugin_b" in rendered


@patch.object(main_module, "localize_app")
@patch.object(main_module, "create_app")
@patch.object(main_module, "load_settings")
def test_main_function(mock_load_settings, mock_create_app, mock_localize_app):
    """测试主入口函数"""
    mock_settings = MagicMock()
    mock_load_settings.return_value = mock_settings
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app

    main_func()

    mock_load_settings.assert_called_once()
    mock_create_app.assert_called_once_with(load_plugin_apps=True)
    mock_localize_app.assert_called_once_with(mock_app, settings=mock_settings)
    mock_app.assert_called_once()
