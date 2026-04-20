from bio_analyze_core.i18n import _
"""Test enhanced Typer framework for parameter passthrough, injection, and extensibility. """
import inspect
import os
from unittest import mock

import pytest
from bio_analyze_core.cli.app import Option, Argument, Context, Exit, echo, prompt, confirm
from bio_analyze_core.cli import BioAnalyzeTyper, CommonParamHandler, get_app
from bio_analyze_core.cli.app import CliRunner

runner = CliRunner()


def test_get_app_passthrough():
    """测试 get_app 正确透传所有初始化参数。"""
    app = get_app(name="test_app", help="Test Help", rich_markup_mode="markdown")
    assert isinstance(app, BioAnalyzeTyper)
    assert app.info.name == "test_app"
    assert app.info.help == "Test Help"
    assert app.rich_markup_mode == "markdown"


def test_native_command_compatibility():
    """测试不注入通用参数时，原生 Typer 行为完全一致。"""
    app = get_app()
    
    @app.command()
    def hello(name: str):
        print(f"Hello {name}")
        
    result = runner.invoke(app, ["world"])
    assert result.exit_code == 0
    assert "Hello world" in result.stdout
    
    # Help 文档不应包含注入参数
    help_result = runner.invoke(app, ["hello", "--help"])
    assert "--verbose" not in help_result.stdout


@mock.patch("bio_analyze_core.cli.app.setup_logging")
def test_inject_verbose_parameter(mock_setup_logging):
    """测试注入 verbose 参数并正确调用处理逻辑。"""
    app = get_app()
    
    @app.command(inject_params=["verbose"])
    def my_cmd(**kwargs):
        print("Cmd executed")
        
    # 测试默认值处理 (False)
    res1 = runner.invoke(app, ["my-cmd"])
    assert res1.exit_code == 0
    mock_setup_logging.assert_called_with(level="INFO")
    
    # 测试传递参数处理 (True)
    res2 = runner.invoke(app, ["my-cmd", "-v"])
    if res2.exit_code != 0:
        print(res2.stdout)
    assert res2.exit_code == 0
    mock_setup_logging.assert_called_with(level="DEBUG")
    
    # Agentyper 将详细模式暴露为 -v；兼容层保留该能力即可。
    help_result = runner.invoke(app, ["my-cmd", "--help"])
    assert "-v" in (help_result.stdout + help_result.stderr)


def test_inject_env_parameter():
    """测试注入 env 参数。"""
    app = get_app()
    
    @app.command(inject_params=["env"])
    def my_env_cmd(**kwargs):
        print(f"Env is: {os.environ.get('BIO_ANALYZE_ENV')}")
        
    res = runner.invoke(app, ["my-env-cmd", "--env", "testing"])
    assert res.exit_code == 0
    assert "Env is: testing" in res.stdout


def test_inject_config_parameter_passthrough():
    """测试当原函数接收 config_dict 参数时，正确透传加载的字典。"""
    app = get_app()
    
    @app.command(inject_params=["config"])
    def my_config_cmd(config_dict: str = "", **kwargs):
        if config_dict:
            print(f"Loaded config keys: {config_dict}")
        else:
            print("No config")
            
    with mock.patch("bio_analyze_core.cli.app.load_config", return_value="parsed_config_data"):
        res = runner.invoke(app, ["my-config-cmd", "--config", "dummy.json"])
        assert res.exit_code == 0
        assert "Loaded config keys: parsed_config_data" in res.stdout


def test_custom_handler_extension():
    """测试自定义通用参数处理器。"""
    
    class TraceHandler(CommonParamHandler):
        param_name = "trace"
        parameter = inspect.Parameter(
            name="trace",
            kind=inspect.Parameter.KEYWORD_ONLY,
            annotation=bool,
            default=False,
        )
        
        def process(self, value, kwargs):
            if value:
                os.environ["CUSTOM_TRACE"] = "1"

    app = get_app()
    app.register_common_param(TraceHandler())
    
    @app.command(inject_params=["trace"])
    def trace_cmd(**kwargs):
        print(f"Trace status: {os.environ.get('CUSTOM_TRACE', '0')}")
        
    # Clear env just in case
    os.environ.pop("CUSTOM_TRACE", None)
    
    res = runner.invoke(app, ["trace-cmd", "--trace"])
    assert res.exit_code == 0
    assert "Trace status: 1" in res.stdout


def test_multi_command_help_with_same_option_names():
    """测试多个命令复用相同选项名时仍能正常显示帮助并分发。"""
    app = get_app(help="Root help")

    @app.command()
    def foo(format: str = Option("a", "--format", help="Foo format")):
        print(f"foo:{format}")

    @app.command()
    def bar(format: str = Option("b", "--format", help="Bar format")):
        print(f"bar:{format}")

    root_help = runner.invoke(app, ["--help"])
    assert root_help.exit_code == 0
    rendered_help = root_help.stdout + root_help.stderr
    assert "foo" in rendered_help
    assert "bar" in rendered_help

    foo_help = runner.invoke(app, ["foo", "--help"])
    assert foo_help.exit_code == 0
    assert "Foo format" in (foo_help.stdout + foo_help.stderr)

    bar_run = runner.invoke(app, ["bar", "--format", "csv"])
    assert bar_run.exit_code == 0
    assert "bar:csv" in bar_run.stdout
