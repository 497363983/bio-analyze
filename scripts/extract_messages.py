from __future__ import annotations

import shutil
from pathlib import Path

from bio_analyze_core.i18n_gettext import DEFAULT_DOMAIN
from bio_analyze_core.subprocess import run

PACKAGES = ("core", "cli", "plot", "docking", "msa", "omics")
ROOT = Path(__file__).resolve().parents[1]


def iter_python_sources(package_root: Path) -> list[str]:
    source_dir = package_root / "src"
    return sorted(path.relative_to(package_root).as_posix() for path in source_dir.rglob("*.py"))


def _build_xgettext_command(xgettext: str, py_files: list[str]) -> list[str]:
    return [
        xgettext,
        "--from-code=UTF-8",
        "--language=Python",
        "--keyword=_",
        "--keyword=pgettext:1c,2",
        "--keyword=ngettext:1,2",
        "--output",
        f"locale/{DEFAULT_DOMAIN}.pot",
        *py_files,
    ]


def main() -> None:
    xgettext = shutil.which("xgettext")
    if not xgettext:
        raise SystemExit(
            "xgettext is required to extract gettext templates. Please install gettext first."
        )

    for package in PACKAGES:
        package_root = ROOT / "packages" / package
        locale_dir = package_root / "locale"
        locale_dir.mkdir(parents=True, exist_ok=True)
        pot_file = locale_dir / f"{DEFAULT_DOMAIN}.pot"
        py_files = iter_python_sources(package_root)
        if not py_files:
            continue

        command = _build_xgettext_command(xgettext, py_files)
        run(command, check=True, cwd=str(package_root))
        print(f"Extracted messages for {package} -> {pot_file}")


if __name__ == "__main__":
    main()
