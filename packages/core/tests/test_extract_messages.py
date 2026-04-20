"""Tests for gettext extraction helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_extract_messages_module():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "scripts" / "extract_messages.py"
    spec = importlib.util.spec_from_file_location("test_extract_messages_module", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_iter_python_sources_returns_package_relative_paths(tmp_path: Path) -> None:
    module = _load_extract_messages_module()
    package_root = tmp_path / "packages" / "demo"
    src_dir = package_root / "src" / "demo_pkg"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "cli.py").write_text("print('demo')\n", encoding="utf-8")

    py_files = module.iter_python_sources(package_root)

    assert py_files == ["src/demo_pkg/__init__.py", "src/demo_pkg/cli.py"]
    assert all(not path.startswith(str(package_root)) for path in py_files)


def test_main_runs_xgettext_from_package_root(monkeypatch, tmp_path: Path) -> None:
    module = _load_extract_messages_module()
    package_root = tmp_path / "packages" / "demo"
    src_dir = package_root / "src" / "demo_pkg"
    src_dir.mkdir(parents=True)
    (src_dir / "cli.py").write_text('_("Run demo")\n', encoding="utf-8")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "PACKAGES", ("demo",))
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/xgettext")

    calls: list[tuple[list[str], dict[str, str | bool]]] = []

    def fake_run(command, **kwargs):
        calls.append((list(command), kwargs))

    monkeypatch.setattr(module, "run", fake_run)

    module.main()

    assert len(calls) == 1
    command, kwargs = calls[0]
    assert kwargs["cwd"] == str(package_root)
    assert kwargs["check"] is True
    assert "locale/messages.pot" in command
    assert "src/demo_pkg/cli.py" in command
    assert str(package_root) not in " ".join(command)
