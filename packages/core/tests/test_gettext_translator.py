from __future__ import annotations

from pathlib import Path

import polib

from bio_analyze_core.i18n_gettext import DEFAULT_LANGUAGE, get_translator


def _write_catalog(base: Path, language: str, msgid: str, msgstr: str, *, context: str | None = None) -> None:
    po_dir = base / language / "LC_MESSAGES"
    po_dir.mkdir(parents=True, exist_ok=True)
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "bio-analyze-test",
        "Content-Type": "text/plain; charset=utf-8",
        "Plural-Forms": "nplurals=2; plural=(n != 1);",
    }
    entry = polib.POEntry(msgid=msgid, msgstr=msgstr, msgctxt=context)
    po.append(entry)
    po_path = po_dir / "messages.po"
    po.save(str(po_path))
    po.save_as_mofile(str(po_dir / "messages.mo"))


def test_translator_fallback_to_english(tmp_path: Path) -> None:
    _write_catalog(tmp_path, "en_US", "Hello", "Hello")
    translator = get_translator(str(tmp_path))
    translator.set_language("fr_FR")
    assert translator.get_language() == "fr_FR"
    assert translator.gettext("Hello") == "Hello"


def test_translator_reads_zh_catalog(tmp_path: Path) -> None:
    _write_catalog(tmp_path, "en_US", "Plot", "Plot")
    _write_catalog(tmp_path, "zh_CN", "Plot", "绘图")
    translator = get_translator(str(tmp_path))
    translator.set_language("zh_CN")
    assert translator.gettext("Plot") == "绘图"


def test_translator_context_translation(tmp_path: Path) -> None:
    _write_catalog(tmp_path, "en_US", "Run", "Run", context="cli")
    _write_catalog(tmp_path, "zh_CN", "Run", "运行", context="cli")
    translator = get_translator(str(tmp_path))
    translator.set_language("zh_CN")
    assert translator.pgettext("cli", "Run") == "运行"


def test_translator_defaults_to_identity(tmp_path: Path) -> None:
    translator = get_translator(str(tmp_path))
    translator.set_language(DEFAULT_LANGUAGE)
    assert translator.gettext("Missing text") == "Missing text"
