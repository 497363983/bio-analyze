"""
Unified CLI compatibility layer built on Agentyper.
"""

from __future__ import annotations

import functools
import inspect
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypeVar, cast, get_args, get_origin, get_type_hints
import agentyper as _cli_framework
from agentyper.testing import CliRunner as _CliRunner
from bio_analyze_core.i18n import _
from bio_analyze_core.logging import setup_logging
from bio_analyze_core.utils import load_config

CliRunner = _CliRunner
_AgentyperExit = _cli_framework.Exit

T = TypeVar("T", bound=Callable[..., Any])
AgentyperBase = _cli_framework.Agentyper
Argument = _cli_framework.Argument
ArgumentInfo = _cli_framework.ArgumentInfo
BadParameter = _cli_framework.BadParameter
Context = _cli_framework.Context


class Exit(_AgentyperExit):
    """Compatibility wrapper that preserves the legacy ``exit_code`` attribute."""

    @property
    def exit_code(self) -> int:
        return self.code


get_current_context = getattr(_cli_framework, "get_current_context", None)
Option = _cli_framework.Option
OptionInfo = _cli_framework.OptionInfo
confirm = _cli_framework.confirm
echo = _cli_framework.echo
prompt = _cli_framework.prompt

_AGENTYPER_INIT_KWARGS = {
    "name",
    "version",
    "help",
    "invoke_without_command",
    "interactive",
    "enable_timeout",
    "default_timeout_ms",
}
_AGENTYPER_COMMAND_KWARGS = {
    "help",
    "mutating",
    "danger_level",
    "exit_codes",
    "requires_editor",
    "non_interactive_alternatives",
    "interactive",
    "timeout_ms",
}
_TRUTHY_VALUES = {"1", "true", "yes", "on"}


@dataclass
class _CallbackParseState:
    callback: Callable[..., Any]
    positional_params: list[inspect.Parameter]
    default_kwargs: dict[str, Any]
    option_specs: dict[str, tuple[inspect.Parameter, OptionInfo, bool | None]]
    resolved_hints: dict[str, Any]


class CommonParamHandler:
    """Base class for dynamically injected common CLI parameters."""

    param_name: str
    parameter: inspect.Parameter

    def process(self, value: Any, kwargs: dict[str, Any]) -> None:
        raise NotImplementedError


class VerboseParamHandler(CommonParamHandler):
    param_name = "verbose"
    parameter = inspect.Parameter(
        name="verbose",
        kind=inspect.Parameter.KEYWORD_ONLY,
        annotation=bool,
        default=Option(
            False,
            "--verbose",
            "-v",
            help=_("Enable verbose output (DEBUG level)."),
            is_flag=True,
        ),
    )

    def process(self, value: bool, kwargs: dict[str, Any]) -> None:
        if get_current_context is not None:
            try:
                context = get_current_context()
                value = bool(value or getattr(getattr(context, "runtime", None), "verbosity", 0))
            except RuntimeError:
                pass
        setup_logging(level="DEBUG" if value else "INFO")


class ConfigParamHandler(CommonParamHandler):
    param_name = "config"
    parameter = inspect.Parameter(
        name="config",
        kind=inspect.Parameter.KEYWORD_ONLY,
        annotation=str | None,
        default=Option(
            None,
            "--config",
            "-c",
            help=_("Path to configuration file (.json, .yaml, .toml)."),
        ),
    )

    def process(self, value: str | None, kwargs: dict[str, Any]) -> None:
        if value and "config_dict" in kwargs:
            kwargs["config_dict"] = load_config(value)


class EnvParamHandler(CommonParamHandler):
    param_name = "env"
    parameter = inspect.Parameter(
        name="env",
        kind=inspect.Parameter.KEYWORD_ONLY,
        annotation=str,
        default=Option(
            "prod",
            "--env",
            "-e",
            help=_("Execution environment (for example dev or prod)."),
        ),
    )

    def process(self, value: str, kwargs: dict[str, Any]) -> None:
        os.environ["BIO_ANALYZE_ENV"] = value


def _normalize_param_declaration(parameter: inspect.Parameter) -> inspect.Parameter:
    """Convert legacy injected parameters into Agentyper-compatible defaults."""
    default = parameter.default
    if isinstance(default, (OptionInfo, ArgumentInfo)):
        return parameter

    cli_name = f"--{parameter.name.replace('_', '-')}"
    if default is inspect.Signature.empty:
        normalized_default = Option(..., cli_name)
    else:
        normalized_default = Option(
            default,
            cli_name,
            is_flag=isinstance(default, bool),
        )
    return parameter.replace(default=normalized_default)


class _CompatCommandInfo:
    def __init__(self, name: str, command_info: Any):
        self.name = name
        self._command_info = command_info

    @property
    def callback(self) -> Any:
        return self._command_info.fn

    @callback.setter
    def callback(self, value: Any) -> None:
        self._command_info.fn = value

    @property
    def help(self) -> str:
        return self._command_info.help

    @help.setter
    def help(self, value: str) -> None:
        self._command_info.help = value


class _CompatGroupInfo:
    def __init__(self, name: str, typer_instance: Any):
        self.name = name
        self.typer_instance = typer_instance

    @property
    def help(self) -> str:
        return self.typer_instance.help

    @help.setter
    def help(self, value: str) -> None:
        self.typer_instance.help = value


class _ManualCommandInfo:
    def __init__(self, name: str, app: BioAnalyzeTyper):
        self.name = name
        self._app = app

    @property
    def callback(self) -> Any:
        return self._app.callback_fn

    @callback.setter
    def callback(self, value: Any) -> None:
        self._app.callback_fn = value

    @property
    def help(self) -> str:
        return self._app.help or ""

    @help.setter
    def help(self, value: str) -> None:
        self._app.help = value


class BioAnalyzeTyper(AgentyperBase):
    """Enhanced Agentyper app with compatibility helpers and parameter injection."""

    def __init__(self, *args: Any, locale_path: str | Path | None = None, **kwargs: Any):
        if args:
            raise TypeError("BioAnalyzeTyper only accepts keyword arguments.")

        init_kwargs = {key: value for key, value in kwargs.items() if key in _AGENTYPER_INIT_KWARGS}
        super().__init__(**init_kwargs)

        extra_init_kwargs = {key: value for key, value in kwargs.items() if key not in _AGENTYPER_INIT_KWARGS}
        for key, value in extra_init_kwargs.items():
            setattr(self, key, value)

        self.rich_markup_mode = extra_init_kwargs.get("rich_markup_mode")
        self.locale_path = str(locale_path) if locale_path is not None else None
        self.translator: Any = None
        self._handlers: dict[str, CommonParamHandler] = {
            "verbose": VerboseParamHandler(),
            "config": ConfigParamHandler(),
            "env": EnvParamHandler(),
        }
        self._compat_commands: dict[str, BioAnalyzeTyper] = {}
        self._compat_groups: dict[str, BioAnalyzeTyper] = {}

    @property
    def info(self) -> SimpleNamespace:
        return SimpleNamespace(name=self.name, help=self.help)

    @property
    def registered_commands(self) -> list[Any]:
        if self._compat_commands:
            return [_ManualCommandInfo(name, app) for name, app in self._compat_commands.items()]
        commands = getattr(self, "_commands", {})
        return [_CompatCommandInfo(name, info) for name, info in commands.items()]

    @property
    def registered_groups(self) -> list[Any]:
        if self._compat_groups:
            return [_CompatGroupInfo(name, sub_app) for name, sub_app in self._compat_groups.items()]
        groups = getattr(self, "_sub_apps", {})
        return [_CompatGroupInfo(name, sub_app) for name, sub_app in groups.items()]

    @property
    def registered_callback(self) -> SimpleNamespace:
        return SimpleNamespace(callback=self.callback_fn)

    @property
    def callback_fn(self) -> Any:
        return getattr(self, "_callback_fn", None)

    @callback_fn.setter
    def callback_fn(self, value: Any) -> None:
        self._callback_fn = value

    def register_common_param(self, handler: CommonParamHandler) -> None:
        self._handlers[handler.param_name] = handler

    def bind_translator(self, translator: Any) -> None:
        self.translator = translator

    def __call__(self, args: list[str] | None = None) -> None:
        normalized_args = list(sys.argv[1:] if args is None else args)
        if self._compat_commands or self._compat_groups:
            self._dispatch_compat(normalized_args)
            return
        if (
            normalized_args
            and normalized_args[0] in {"-h", "--help", "help"}
            and self.callback_fn is not None
            and not getattr(self, "_commands", {})
        ):
            self._render_callback_help()
            return
        injected_command = self._resolve_single_command_name(normalized_args)
        if injected_command is not None:
            normalized_args.insert(0, injected_command)
        super().__call__(normalized_args)

    def _dispatch_compat(self, args: list[str]) -> None:
        if not args or args[0] in {"-h", "--help", "help"}:
            self._render_compat_help()
            return

        callback = self.callback_fn
        if callback is not None:
            callback()

        token = args[0]
        if token in self._compat_groups:
            child = self._compat_groups[token]
            child(args[1:] or ["--help"])
            return
        if token in self._compat_commands:
            child = self._compat_commands[token]
            child.invoke_callback_compat(args[1:])
            return

        if len(self._compat_commands) == 1 and not self._compat_groups and not token.startswith("-"):
            only_child = next(iter(self._compat_commands.values()))
            only_child.invoke_callback_compat(args)
            return

        raise Exit(2)

    def _render_compat_help(self) -> None:
        if self.help:
            echo(self.help)
            echo("")
        if self._compat_groups:
            echo("Groups:")
            for name, group in self._compat_groups.items():
                echo(f"  {name}\t{group.help or ''}")
        if self._compat_commands:
            if self._compat_groups:
                echo("")
            echo("Commands:")
            for name, command in self._compat_commands.items():
                echo(f"  {name}\t{command.help or ''}")

    def _render_callback_help(self) -> None:
        if self.help:
            echo(self.help)
            echo("")
        callback = self.callback_fn
        if callback is None:
            return
        options: list[str] = []
        arguments: list[str] = []
        for name, param in inspect.signature(callback).parameters.items():
            if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                continue
            decls, help_text, is_argument = self._describe_callback_param(name, param)
            target = arguments if is_argument else options
            target.append(f"  {decls}\t{help_text}")
        if arguments:
            echo("Args:")
            for line in arguments:
                echo(line)
        if options:
            if arguments:
                echo("")
            echo("Options:")
            for line in options:
                echo(line)

    def _invoke_callback(self, args: list[str]) -> None:
        if args and args[0] in {"-h", "--help", "help"}:
            self._render_callback_help()
            return

        callback = self.callback_fn
        if callback is None or not callable(callback):
            raise Exit(2)

        parse_state = self._build_callback_parse_state(callback)
        parsed_options: dict[str, Any] = {}
        parsed_positionals: list[Any] = []

        index = 0
        positional_index = 0
        while index < len(args):
            token = args[index]
            if token.startswith("-"):
                index = self._consume_option_token(
                    args=args,
                    index=index,
                    parse_state=parse_state,
                    parsed_options=parsed_options,
                )
                continue

            if positional_index >= len(parse_state.positional_params):
                raise Exit(2)
            param = parse_state.positional_params[positional_index]
            annotation = parse_state.resolved_hints.get(param.name, param.annotation)
            parsed_positionals.append(self._coerce_value(token, annotation))
            positional_index += 1
            index += 1

        self._append_missing_positionals(
            parse_state.positional_params,
            positional_index,
            parsed_positionals,
        )
        self._apply_callback_defaults(parse_state, parsed_options)
        parse_state.callback(*parsed_positionals, **parsed_options)

    def invoke_callback_compat(self, args: list[str]) -> None:
        self._invoke_callback(args)

    def _coerce_value(self, value: str, annotation: Any) -> Any:
        result: Any = value
        if annotation in {inspect.Signature.empty, Any, str}:
            return result

        if isinstance(annotation, str):
            return self._coerce_string_annotation(value, annotation)

        converter = {
            int: int,
            float: float,
            Path: Path,
        }.get(annotation)
        origin = get_origin(annotation)

        if converter is not None:
            result = converter(value)
        elif annotation is bool:
            result = value.lower() in _TRUTHY_VALUES
        elif origin is list:
            result = self._split_csv(value)
        elif origin is tuple:
            result = tuple(self._split_csv(value))
        elif origin is not dict:
            optional_args = self._non_none_type_args(annotation, origin)
            if optional_args:
                result = self._coerce_value(value, optional_args[0])
        return result

    def add_typer(self, agentyper: BioAnalyzeTyper, *, name: str) -> None:
        self._compat_groups[name] = agentyper

    def command(
        self,
        *args: Any,
        name: str | None = None,
        inject_params: list[str] | None = None,
        **kwargs: Any,
    ):
        command_name = self._resolve_command_name(args, name)

        command_kwargs = {key: value for key, value in kwargs.items() if key in _AGENTYPER_COMMAND_KWARGS}

        def decorator(func: T) -> T:
            resolved_name = command_name or func.__name__.strip("_").replace("_", "-")
            command_app = self._create_command_app(resolved_name, command_kwargs.get("help"))
            orig_decorator_factory = command_app.callback(invoke_without_command=True)
            if not inject_params:
                self._compat_commands[resolved_name] = command_app
                return orig_decorator_factory(func)

            sig = inspect.signature(func)
            params, active_handlers = self._inject_common_params(sig, inject_params)
            if not active_handlers:
                self._compat_commands[resolved_name] = command_app
                return orig_decorator_factory(func)

            new_sig = sig.replace(parameters=params)
            wrapper = self._build_injected_wrapper(func, sig, new_sig, active_handlers)

            self._compat_commands[resolved_name] = command_app
            return orig_decorator_factory(wrapper)  # type: ignore[return-value]

        return decorator

    def _resolve_single_command_name(self, normalized_args: list[str]) -> str | None:
        commands = getattr(self, "_commands", {})
        groups = getattr(self, "_sub_apps", {})
        if len(commands) != 1 or groups:
            return None

        only_name = next(iter(commands))
        known_names = set(commands) | set(groups)
        if not normalized_args:
            return only_name
        if normalized_args[0].startswith("-"):
            return only_name
        if normalized_args[0] not in known_names:
            return only_name
        return None

    def _describe_callback_param(
        self,
        name: str,
        param: inspect.Parameter,
    ) -> tuple[str, str, bool]:
        default = param.default
        if isinstance(default, OptionInfo):
            decls = ", ".join(getattr(default, "param_decls", ()) or [f"--{name.replace('_', '-')}"])
            return decls, getattr(default, "help", ""), False
        if isinstance(default, ArgumentInfo):
            return name, getattr(default, "help", ""), True
        decls = name if default is inspect.Signature.empty else f"--{name.replace('_', '-')}"
        help_text = ""
        return decls, help_text, default is inspect.Signature.empty

    def _build_callback_parse_state(self, callback: Callable[..., Any]) -> _CallbackParseState:
        positional_params: list[inspect.Parameter] = []
        default_kwargs: dict[str, Any] = {}
        option_specs: dict[str, tuple[inspect.Parameter, OptionInfo, bool | None]] = {}
        resolved_hints = get_type_hints(callback)

        for param in inspect.signature(callback).parameters.values():
            if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                continue
            default = param.default
            if isinstance(default, OptionInfo):
                self._register_option_specs(option_specs, param, default)
                continue
            if isinstance(default, ArgumentInfo) or default is inspect.Signature.empty:
                positional_params.append(param)
                continue
            default_kwargs[param.name] = default

        return _CallbackParseState(
            callback=callback,
            positional_params=positional_params,
            default_kwargs=default_kwargs,
            option_specs=option_specs,
            resolved_hints=resolved_hints,
        )

    def _register_option_specs(
        self,
        option_specs: dict[str, tuple[inspect.Parameter, OptionInfo, bool | None]],
        param: inspect.Parameter,
        default: OptionInfo,
    ) -> None:
        decls = getattr(default, "param_decls", ()) or [f"--{param.name.replace('_', '-')}"]
        for decl in decls:
            if "/" in decl:
                true_decl, false_decl = decl.split("/", 1)
                option_specs[true_decl] = (param, default, True)
                option_specs[false_decl] = (param, default, False)
                continue
            option_specs[decl] = (param, default, None)

    def _consume_option_token(
        self,
        *,
        args: list[str],
        index: int,
        parse_state: _CallbackParseState,
        parsed_options: dict[str, Any],
    ) -> int:
        token = args[index]
        spec = parse_state.option_specs.get(token)
        if spec is None:
            raise Exit(2)

        param, default, bool_override = spec
        if bool_override is not None:
            parsed_options[param.name] = bool_override
            return index + 1

        annotation = parse_state.resolved_hints.get(param.name, param.annotation)
        next_token = args[index + 1] if index + 1 < len(args) else None
        if self._is_flag_without_value(annotation, default, next_token):
            parsed_options[param.name] = True
            return index + 1
        if next_token is None:
            raise Exit(2)
        parsed_options[param.name] = self._coerce_value(next_token, annotation)
        return index + 2

    def _is_flag_without_value(
        self,
        annotation: Any,
        default: OptionInfo,
        next_token: str | None,
    ) -> bool:
        is_bool_option = annotation is bool or isinstance(getattr(default, "default", None), bool)
        return is_bool_option and (next_token is None or next_token.startswith("-"))

    def _append_missing_positionals(
        self,
        positional_params: list[inspect.Parameter],
        positional_index: int,
        parsed_positionals: list[Any],
    ) -> None:
        for param in positional_params[positional_index:]:
            if param.default is inspect.Signature.empty:
                raise Exit(2)
            parsed_positionals.append(param.default)

    def _apply_callback_defaults(
        self,
        parse_state: _CallbackParseState,
        parsed_options: dict[str, Any],
    ) -> None:
        for param in inspect.signature(parse_state.callback).parameters.values():
            if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                continue
            if param.name in parsed_options:
                continue
            default = param.default
            if isinstance(default, OptionInfo):
                if default.default is ...:
                    raise Exit(2)
                parsed_options[param.name] = default.default
                continue
            if param.name in parse_state.default_kwargs:
                parsed_options[param.name] = parse_state.default_kwargs[param.name]

    def _coerce_string_annotation(self, value: str, annotation: str) -> Any:
        normalized = annotation.replace(" ", "")
        if normalized in {"Path", "pathlib.Path"}:
            return Path(value)
        if normalized == "int":
            return int(value)
        if normalized == "float":
            return float(value)
        if normalized == "bool":
            return value.lower() in _TRUTHY_VALUES
        if normalized in {"list[str]", "list[str|None]"}:
            return self._split_csv(value)
        return value

    def _split_csv(self, value: str) -> list[str]:
        return [part.strip() for part in value.split(",") if part.strip()]

    def _non_none_type_args(self, annotation: Any, origin: Any) -> list[Any]:
        if origin is not None or not hasattr(annotation, "__args__"):
            return []
        return [arg for arg in get_args(annotation) if arg is not type(None)]

    def _resolve_command_name(
        self,
        args: tuple[Any, ...],
        name: str | None,
    ) -> str | None:
        if len(args) > 1:
            raise TypeError("BioAnalyzeTyper.command() accepts at most one positional argument for the command name.")
        if not args:
            return name
        if name is not None:
            raise TypeError("Command name cannot be provided both positionally and by keyword.")
        return cast(str, args[0])

    def _create_command_app(self, resolved_name: str, help_text: str | None) -> BioAnalyzeTyper:
        command_app = BioAnalyzeTyper(
            name=resolved_name,
            help=help_text,
            locale_path=self.locale_path,
        )
        command_app.translator = self.translator
        return command_app

    def _inject_common_params(
        self,
        sig: inspect.Signature,
        inject_params: list[str] | None,
    ) -> tuple[list[inspect.Parameter], list[CommonParamHandler]]:
        params = [param for param in sig.parameters.values() if param.kind != inspect.Parameter.VAR_KEYWORD]
        existing_param_names = {param.name for param in params}
        active_handlers: list[CommonParamHandler] = []
        insert_pos = self._injected_param_insert_pos(params)

        for param_name in inject_params or []:
            handler = self._handlers.get(param_name)
            if handler is None:
                raise ValueError(f"Unknown common parameter: '{param_name}'")
            if param_name in existing_param_names:
                continue
            params.insert(insert_pos, _normalize_param_declaration(handler.parameter))
            insert_pos += 1
            active_handlers.append(handler)
        return params, active_handlers

    def _injected_param_insert_pos(self, params: list[inspect.Parameter]) -> int:
        for index, param in enumerate(params):
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                return index + 1
        return len(params)

    def _build_injected_wrapper(
        self,
        func: T,
        sig: inspect.Signature,
        new_sig: inspect.Signature,
        active_handlers: list[CommonParamHandler],
    ) -> T:
        @functools.wraps(func)
        def wrapper(*w_args: Any, **w_kwargs: Any) -> Any:
            self._apply_config_default(sig, w_kwargs)
            self._process_common_handlers(active_handlers, w_kwargs)
            return func(*w_args, **w_kwargs)

        wrapper_func = cast(Any, wrapper)
        wrapper_func.__signature__ = new_sig
        if wrapper_func.__kwdefaults__ is None:
            wrapper_func.__kwdefaults__ = {}
        self._apply_wrapper_handler_metadata(wrapper_func, active_handlers)
        if hasattr(func, "__defaults__"):
            wrapper_func.__defaults__ = func.__defaults__
        return cast(T, wrapper)

    def _apply_config_default(
        self,
        sig: inspect.Signature,
        w_kwargs: dict[str, Any],
    ) -> None:
        if "config_dict" not in sig.parameters or "config_dict" in w_kwargs:
            return
        config_param = sig.parameters["config_dict"]
        if config_param.default is not inspect.Signature.empty:
            w_kwargs["config_dict"] = config_param.default

    def _process_common_handlers(
        self,
        active_handlers: list[CommonParamHandler],
        w_kwargs: dict[str, Any],
    ) -> None:
        for handler in active_handlers:
            value = self._resolve_handler_value(handler, w_kwargs)
            handler.process(value, w_kwargs)

    def _resolve_handler_value(
        self,
        handler: CommonParamHandler,
        w_kwargs: dict[str, Any],
    ) -> Any:
        if handler.param_name in w_kwargs:
            return w_kwargs.pop(handler.param_name)
        default_value = _normalize_param_declaration(handler.parameter).default
        if isinstance(default_value, (OptionInfo, ArgumentInfo)):
            return default_value.default
        return default_value

    def _apply_wrapper_handler_metadata(
        self,
        wrapper_func: Any,
        active_handlers: list[CommonParamHandler],
    ) -> None:
        for handler in active_handlers:
            declared_parameter = _normalize_param_declaration(handler.parameter)
            wrapper_func.__annotations__[handler.param_name] = declared_parameter.annotation
            wrapper_func.__kwdefaults__[handler.param_name] = declared_parameter.default


def get_app(*args: Any, **kwargs: Any) -> BioAnalyzeTyper:
    """Factory method returning an enhanced BioAnalyzeTyper instance."""
    if args:
        raise TypeError("get_app only accepts keyword arguments.")
    return BioAnalyzeTyper(**kwargs)


__all__ = [
    "Argument",
    "ArgumentInfo",
    "BadParameter",
    "BioAnalyzeTyper",
    "CliRunner",
    "CommonParamHandler",
    "Context",
    "Exit",
    "Option",
    "OptionInfo",
    "confirm",
    "echo",
    "get_app",
    "prompt",
]
