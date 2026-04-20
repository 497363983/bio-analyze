from __future__ import annotations

from pathlib import Path

import polib

from bio_analyze_core.cli import get_app
from bio_analyze_core.cli.app import CliRunner, Option
from bio_analyze_core.cli_i18n import localize_app
from bio_analyze_core.config import Settings


def _write_translation(base: Path, language: str, msgid: str, msgstr: str) -> None:
    po_dir = base / language / "LC_MESSAGES"
    po_dir.mkdir(parents=True, exist_ok=True)
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "bio-analyze-test",
        "Content-Type": "text/plain; charset=utf-8",
        "Plural-Forms": "nplurals=2; plural=(n != 1);",
    }
    po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))
    po.save(str(po_dir / "messages.po"))
    po.save_as_mofile(str(po_dir / "messages.mo"))


def test_localize_app_translates_help(tmp_path: Path) -> None:
    _write_translation(tmp_path, "en_US", "Plot things", "Plot things")
    _write_translation(tmp_path, "zh_CN", "Plot things", "绘图工具")
    _write_translation(tmp_path, "en_US", "Input file", "Input file")
    _write_translation(tmp_path, "zh_CN", "Input file", "输入文件")

    app = get_app(help="Plot things", locale_path=tmp_path)

    @app.command()
    def plot(input_file: str = Option(..., "--input", help="Input file")) -> None:
        """Plot things."""

    localize_app(app, settings=Settings(language="zh_CN", dev_mode=False))
    result = CliRunner().invoke(app, ["plot", "--help"])
    rendered = result.stdout + result.stderr
    assert result.exit_code == 0
    assert "输入文件" in rendered
