from __future__ import annotations

import inspect
from typing import Any


def get_param_type(param: inspect.Parameter) -> str:
    if param.annotation == inspect.Parameter.empty:
        return "any"

    annotation = str(param.annotation)
    if "Path" in annotation:
        return "path"
    if "int" in annotation:
        return "int"
    if "float" in annotation:
        return "float"
    if "bool" in annotation:
        return "bool"
    if "str" in annotation:
        return "string"
    if "list" in annotation or "List" in annotation:
        return "list"
    if "dict" in annotation or "Dict" in annotation:
        return "dict"
    return annotation.replace("typing.", "").replace("<class '", "").replace("'>", "")


def _normalize_text(text: str) -> str:
    return text or ""


def build_command_schema(command_info: Any, cmd_name: str) -> dict[str, Any]:
    callback = command_info.callback
    if not callback:
        return {"name": cmd_name, "type": "cli", "description": "", "params": []}

    params_list = []
    sig = inspect.signature(callback)
    for name, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        default = param.default
        help_text = _normalize_text(getattr(default, "help", ""))
        param_opts = list(getattr(default, "param_decls", ()) or ())
        real_default = getattr(default, "default", default)
        if real_default in (inspect.Parameter.empty, ...):
            real_default = None

        params_list.append(
            {
                "field": name,
                "name": ", ".join(param_opts) if param_opts else f"--{name.replace('_', '-')}",
                "type": get_param_type(param),
                "required": param.default == inspect.Parameter.empty or getattr(default, "default", None) == ...,
                "default": str(real_default) if real_default is not None else None,
                "description": help_text,
            }
        )

    description = _normalize_text(command_info.help or inspect.getdoc(callback) or "")
    return {
        "name": cmd_name,
        "type": "cli",
        "description": description,
        "params": params_list,
    }


def build_cli_schema(app: Any, prefix: str = "") -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for command_info in app.registered_commands:
        cmd_name = command_info.name or getattr(command_info.callback, "__name__", "").strip("_")
        if not cmd_name:
            continue
        entries.append(build_command_schema(command_info, f"{prefix}{cmd_name}"))

    for group_info in app.registered_groups:
        if group_info.typer_instance:
            next_prefix = f"{prefix}{group_info.name}_" if group_info.name else prefix
            entries.extend(build_cli_schema(group_info.typer_instance, next_prefix))
    return entries
