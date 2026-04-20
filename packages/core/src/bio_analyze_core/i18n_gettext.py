from __future__ import annotations

import gettext
import os
from contextlib import contextmanager
from contextvars import ContextVar
from io import BytesIO
from pathlib import Path
from typing import Protocol

import polib

DEFAULT_DOMAIN = "messages"
DEFAULT_LANGUAGE = "en_US"
_current_translator: ContextVar[Translator | None] = ContextVar(
    "bio_analyze_current_translator",
    default=None,
)
_translator_cache: dict[tuple[str, str], GettextTranslator] = {}


class Translator(Protocol):
    def gettext(self, message: str) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int) -> str: ...
    def pgettext(self, context: str, message: str) -> str: ...
    def set_language(self, language: str) -> None: ...
    def get_language(self) -> str: ...
    def set_dev_mode(self, enabled: bool) -> None: ...
    def reload_if_needed(self) -> None: ...


def _normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_LANGUAGE
    normalized = language.split(".")[0].replace("-", "_")
    if normalized.lower().startswith("zh"):
        return "zh_CN"
    if normalized.lower().startswith("en"):
        return "en_US"
    return normalized


def _normalize_locale_path(locale_path: str | Path) -> Path:
    return Path(locale_path).expanduser().resolve()


class GettextTranslator:
    def __init__(self, locale_path: str | Path, domain: str = DEFAULT_DOMAIN):
        self.locale_path = _normalize_locale_path(locale_path)
        self.domain = domain
        self._language = DEFAULT_LANGUAGE
        self._dev_mode = False
        self._translations: dict[tuple[str, bool], gettext.NullTranslations] = {}
        self._mtimes: dict[tuple[str, bool], tuple[float | None, float | None]] = {}

    def set_language(self, language: str) -> None:
        self._language = _normalize_language(language)

    def get_language(self) -> str:
        return self._language

    def set_dev_mode(self, enabled: bool) -> None:
        self._dev_mode = enabled

    def gettext(self, message: str) -> str:
        self.reload_if_needed()
        return self._get_translation().gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        self.reload_if_needed()
        return self._get_translation().ngettext(singular, plural, n)

    def pgettext(self, context: str, message: str) -> str:
        self.reload_if_needed()
        translation = self._get_translation()
        if hasattr(translation, "pgettext"):
            return translation.pgettext(context, message)
        combined = f"{context}\x04{message}"
        resolved = translation.gettext(combined)
        if resolved == combined:
            return message
        return resolved

    def reload_if_needed(self) -> None:
        cache_key = (self._language, self._dev_mode)
        current_mtimes = self._get_mtimes(self._language, self._dev_mode)
        if self._mtimes.get(cache_key) != current_mtimes:
            self._translations.pop(cache_key, None)

    def _get_translation(self) -> gettext.NullTranslations:
        cache_key = (self._language, self._dev_mode)
        if cache_key not in self._translations:
            self._translations[cache_key] = self._load_translation(self._language, self._dev_mode)
            self._mtimes[cache_key] = self._get_mtimes(self._language, self._dev_mode)
        return self._translations[cache_key]

    def _get_mtimes(self, language: str, dev_mode: bool) -> tuple[float | None, float | None]:
        mo_path = self.locale_path / language / "LC_MESSAGES" / f"{self.domain}.mo"
        po_path = self.locale_path / language / "LC_MESSAGES" / f"{self.domain}.po"
        return (
            mo_path.stat().st_mtime if mo_path.exists() else None,
            po_path.stat().st_mtime if dev_mode and po_path.exists() else None,
        )

    def _load_translation(self, language: str, dev_mode: bool) -> gettext.NullTranslations:
        candidates = [language]
        if language != DEFAULT_LANGUAGE:
            candidates.append(DEFAULT_LANGUAGE)

        for candidate in candidates:
            translation = self._load_candidate(candidate, dev_mode)
            if translation is not None:
                return translation
        return gettext.NullTranslations()

    def _load_candidate(self, language: str, dev_mode: bool) -> gettext.NullTranslations | None:
        mo_path = self.locale_path / language / "LC_MESSAGES" / f"{self.domain}.mo"
        po_path = self.locale_path / language / "LC_MESSAGES" / f"{self.domain}.po"

        if dev_mode and po_path.exists():
            catalog = polib.pofile(str(po_path))
            return gettext.GNUTranslations(BytesIO(catalog.to_binary()))
        if mo_path.exists():
            with mo_path.open("rb") as handle:
                return gettext.GNUTranslations(handle)
        return None


def get_translator(locale_path: str) -> Translator:
    resolved = str(_normalize_locale_path(locale_path))
    cache_key = (resolved, DEFAULT_DOMAIN)
    if cache_key not in _translator_cache:
        _translator_cache[cache_key] = GettextTranslator(resolved, domain=DEFAULT_DOMAIN)
    return _translator_cache[cache_key]


def get_current_translator() -> Translator | None:
    return _current_translator.get()


def set_current_translator(translator: Translator | None) -> None:
    _current_translator.set(translator)


@contextmanager
def use_translator(translator: Translator | None):
    token = _current_translator.set(translator)
    try:
        yield
    finally:
        _current_translator.reset(token)


def resolve_locale_from_environment() -> str:
    for env_name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(env_name)
        if value:
            return _normalize_language(value)
    return DEFAULT_LANGUAGE
