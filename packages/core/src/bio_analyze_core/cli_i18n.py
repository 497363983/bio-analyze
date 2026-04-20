from __future__ import annotations

import functools
import inspect
from typing import Any, cast

from .cli.app import ArgumentInfo, OptionInfo
from .config import Settings
from .i18n_gettext import Translator, get_translator, resolve_locale_from_environment, use_translator


def _normalize_source_text(text: str) -> str:
    return text or ""


def resolve_language(settings: Settings | None = None, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    if settings and settings.language:
        return settings.language
    return resolve_locale_from_environment()


def detect_language() -> str:
    return resolve_language()


def localize_app(
    app: Any,
    lang: str | None = None,
    settings: Settings | None = None,
    translator: Translator | None = None,
) -> None:
    active_translator = translator
    if active_translator is None:
        active_translator = getattr(app, "translator", None)
    if active_translator is None:
        locale_path = getattr(app, "locale_path", None)
        if locale_path:
            active_translator = get_translator(locale_path)
    if active_translator is None:
        return

    active_translator.set_language(resolve_language(settings, lang))
    if hasattr(active_translator, "set_dev_mode"):
        active_translator.set_dev_mode(bool(settings.dev_mode) if settings else False)
    if hasattr(app, "bind_translator"):
        app.bind_translator(active_translator)

    if getattr(app, "help", None):
        app.help = _translate_text(app.help, active_translator)

    for cmd_info in app.registered_commands:
        if cmd_info.help:
            cmd_info.help = _translate_text(cmd_info.help, active_translator)
        elif cmd_info.callback and cmd_info.callback.__doc__:
            cmd_info.help = _translate_text(inspect.getdoc(cmd_info.callback) or "", active_translator)
        if cmd_info.callback:
            if cmd_info.callback.__doc__:
                cmd_info.callback.__doc__ = _translate_text(inspect.getdoc(cmd_info.callback) or "", active_translator)
            _localize_callback(cmd_info.callback, active_translator)
            cmd_info.callback = _wrap_callback(cmd_info.callback, active_translator)

    for group_info in app.registered_groups:
        if group_info.help:
            group_info.help = _translate_text(group_info.help, active_translator)
        if group_info.typer_instance:
            group_translator = getattr(group_info.typer_instance, "translator", active_translator)
            localize_app(group_info.typer_instance, settings=settings, translator=group_translator)


def _wrap_callback(callback: Any, translator: Translator) -> Any:
    if getattr(callback, "__bio_analyze_wrapped__", False):
        return callback

    @functools.wraps(callback)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with use_translator(translator):
            return callback(*args, **kwargs)

    wrapped_callback = cast(Any, wrapper)
    wrapped_callback.__bio_analyze_wrapped__ = True
    wrapped_callback.__signature__ = inspect.signature(callback)
    if hasattr(callback, "__defaults__"):
        wrapped_callback.__defaults__ = callback.__defaults__
    if hasattr(callback, "__kwdefaults__"):
        wrapped_callback.__kwdefaults__ = callback.__kwdefaults__
    return wrapped_callback


def _translate_text(text: str, translator: Translator) -> str:
    source = _normalize_source_text(text)
    return translator.gettext(source)


def _localize_callback(callback: Any, translator: Translator) -> None:
    if callback.__defaults__:
        for default in callback.__defaults__:
            _localize_param_info(default, translator)
    if callback.__kwdefaults__:
        for default in callback.__kwdefaults__.values():
            _localize_param_info(default, translator)


def _localize_param_info(param: Any, translator: Translator) -> None:
    if isinstance(param, (OptionInfo, ArgumentInfo)) and param.help:
        param.help = _translate_text(param.help, translator)
