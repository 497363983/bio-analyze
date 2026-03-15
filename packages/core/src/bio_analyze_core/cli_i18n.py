from __future__ import annotations

import os
from typing import Any

import typer
from typer.models import ArgumentInfo, OptionInfo

from .i18n import get_target_text


def detect_language() -> str:
    """
    Detect the preferred language for the CLI.
    Priority:
    1. BIO_ANALYZE_LANG environment variable
    2. LANG / LC_ALL environment variables (simple check)
    3. Default to 'en'
    """
    # 1. Specific Env Var
    lang = os.environ.get("BIO_ANALYZE_LANG")
    if lang:
        return lang.lower()

    # 2. System Locale
    # This is a basic check. Python's locale module is more robust but environment vars are often enough for CLI tools.
    sys_lang = os.environ.get("LANG", "") or os.environ.get("LC_ALL", "")
    if "zh" in sys_lang.lower() or "cn" in sys_lang.lower():
        return "zh"

    # 3. Default
    return "en"


def localize_app(app: typer.Typer, lang: str | None = None) -> None:
    """
    In-place localize the Typer app by filtering help strings.

    Args:
        app: The Typer application instance.
        lang: Target language ('zh' or 'en'). If None, auto-detects.
    """
    if lang is None:
        lang = detect_language()

    # If language is English (default), and we assume strings are "zh... en...",
    # we still need to process them to remove the zh part.
    # So we always run this.

    # 1. Localize Commands
    for cmd_info in app.registered_commands:
        if cmd_info.help:
            cmd_info.help = get_target_text(cmd_info.help, lang)
        elif cmd_info.callback and cmd_info.callback.__doc__:
            cmd_info.callback.__doc__ = get_target_text(cmd_info.callback.__doc__, lang)

        # Localize Callback Parameters
        if cmd_info.callback:
            _localize_callback(cmd_info.callback, lang)

    # 2. Localize Sub-groups (Typer instances)
    for group_info in app.registered_groups:
        if group_info.help:
            group_info.help = get_target_text(group_info.help, lang)

        if group_info.typer_instance:
            # Also localize the main help of the sub-typer if not set in group_info
            if not group_info.help and group_info.typer_instance.info.help:
                group_info.typer_instance.info.help = get_target_text(group_info.typer_instance.info.help, lang)

            localize_app(group_info.typer_instance, lang)


def _localize_callback(callback: Any, lang: str) -> None:
    """
    Inspect a callback function and update its default values (OptionInfo/ArgumentInfo).
    """
    # We need to access the defaults of the function.
    # Typer reads from __defaults__ (positional args) and __kwdefaults__ (keyword-only args).

    # 1. Handle __defaults__
    if callback.__defaults__:
        new_defaults = []
        for default in callback.__defaults__:
            _localize_param_info(default, lang)
            new_defaults.append(default)
        # We modified objects in place, so re-assignment might not be strictly necessary
        # if the tuple holds references to mutable objects.
        # But tuple itself is immutable. The objects inside OptionInfo are mutable.
        pass

    # 2. Handle __kwdefaults__
    if callback.__kwdefaults__:
        for key, default in callback.__kwdefaults__.items():
            _localize_param_info(default, lang)


def _localize_param_info(param: Any, lang: str) -> None:
    """
    Update help text in OptionInfo or ArgumentInfo.
    """
    if isinstance(param, (OptionInfo, ArgumentInfo)):
        if param.help:
            # We modify the object in-place.
            # Since these objects are created at definition time and stored in the function defaults,
            # this change persists for the runtime of the process.
            param.help = get_target_text(param.help, lang)
