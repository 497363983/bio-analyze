from __future__ import annotations

from pathlib import Path

import polib

PACKAGES = ("core", "cli", "plot", "docking", "msa", "omics")
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for package in PACKAGES:
        locale_dir = ROOT / "packages" / package / "locale"
        for po_file in locale_dir.glob("*/LC_MESSAGES/messages.po"):
            mo_file = po_file.with_suffix(".mo")
            catalog = polib.pofile(str(po_file))
            catalog.save_as_mofile(str(mo_file))
            print(f"Compiled {po_file} -> {mo_file}")


if __name__ == "__main__":
    main()
