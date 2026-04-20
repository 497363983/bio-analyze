from unittest.mock import MagicMock, patch

import pytest
from bio_analyze_core.cli.app import BioAnalyzeTyper

from bio_analyze_cli.plugins import CliPlugin, _load_typer, attach_plugins, load_plugins


def test_load_typer_with_typer_instance():
    """测试 _load_typer 接收 BioAnalyzeTyper 实例"""
    app = BioAnalyzeTyper()
    assert _load_typer(app) is app


def test_load_typer_with_callable_returning_typer():
    """测试 _load_typer 接收返回 BioAnalyzeTyper 的可调用对象"""
    app = BioAnalyzeTyper()

    def get_app():
        return app

    assert _load_typer(get_app) is app


def test_load_typer_with_invalid_object():
    """测试 _load_typer 接收无效对象时抛出 TypeError"""
    with pytest.raises(TypeError, match=r"CLI plugin must be a BioAnalyzeTyper app or a callable returning a BioAnalyzeTyper app\."):
        _load_typer("not an app")

    def get_invalid_app():
        return "not an app"

    with pytest.raises(TypeError, match=r"CLI plugin must be a BioAnalyzeTyper app or a callable returning a BioAnalyzeTyper app\."):
        _load_typer(get_invalid_app)


@patch("bio_analyze_cli.plugins._iter_entry_points")
def test_load_plugins(mock_iter_entry_points):
    """测试 load_plugins 从 entry points 加载插件"""
    # 模拟两个 entry point
    app1 = BioAnalyzeTyper()
    app2 = BioAnalyzeTyper()

    ep1 = MagicMock()
    ep1.name = "plugin_b"
    ep1.load.return_value = app1

    ep2 = MagicMock()
    ep2.name = "plugin_a"
    ep2.load.return_value = lambda: app2

    mock_iter_entry_points.return_value = [ep1, ep2]

    plugins = load_plugins()

    # 应该按名称排序
    assert len(plugins) == 2
    assert plugins[0].name == "plugin_a"
    assert plugins[0].app is app2
    assert plugins[1].name == "plugin_b"
    assert plugins[1].app is app1


@patch("bio_analyze_cli.plugins.load_plugins")
def test_attach_plugins(mock_load_plugins):
    """测试 attach_plugins 将插件挂载到根命令"""
    app1 = BioAnalyzeTyper()
    app2 = BioAnalyzeTyper()

    mock_load_plugins.return_value = [
        CliPlugin(name="plugin_a", app=app1),
        CliPlugin(name="plugin_b", app=app2),
    ]

    root_app = BioAnalyzeTyper()

    # 挂载前注册的命令组应该是空的
    assert len(root_app.registered_groups) == 0

    attach_plugins(root_app)

    # 挂载后应该有两个命令组
    assert len(root_app.registered_groups) == 2
    names = [group.name for group in root_app.registered_groups]
    assert "plugin_a" in names
    assert "plugin_b" in names
