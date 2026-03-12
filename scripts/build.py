#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def build_package(package_dir: Path):
    """使用 uv build 构建单个包。"""
    print(f"Building package: {package_dir.name}...")
    try:
        # 检查包是否存在
        if not package_dir.exists():
            print(f"Error: Package directory {package_dir} does not exist.")
            sys.exit(1)

        # 清理包的 dist 目录
        pkg_dist = package_dir / "dist"
        if pkg_dist.exists():
            shutil.rmtree(pkg_dist)

        subprocess.run(["uv", "build"], cwd=package_dir, check=True)
        print(f"Successfully built {package_dir.name}")
        return pkg_dist
    except subprocess.CalledProcessError as e:
        print(f"Failed to build {package_dir.name}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build bio-analyze packages.")
    parser.add_argument(
        "packages",
        nargs="*",
        help="Specific packages to build (e.g., 'core', 'cli'). If empty, builds all.",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    packages_dir = root_dir / "packages"
    dist_dir = root_dir / "dist"

    # 如果不存在则创建 dist 目录（如果构建特定包，是否不清理？）
    # 如果构建所有，清理。如果特定，也许保留其他的？
    # 为了简单起见，如果 args.packages 为空（构建所有），则清理 dist。
    if not args.packages:
        if dist_dir.exists():
            print(f"Cleaning dist directory: {dist_dir}")
            shutil.rmtree(dist_dir)
        dist_dir.mkdir()
    else:
        dist_dir.mkdir(exist_ok=True)

    # 确定要构建哪些包
    all_packages = [p for p in packages_dir.iterdir() if p.is_dir() and (p / "pyproject.toml").exists()]

    target_packages = []
    if args.packages:
        for name in args.packages:
            pkg_path = packages_dir / name
            if pkg_path in all_packages:
                target_packages.append(pkg_path)
            else:
                print(f"Warning: Package '{name}' not found in {packages_dir}. Skipping.")
    else:
        target_packages = all_packages

    if not target_packages:
        print("No valid packages selected to build.")
        sys.exit(0)

    print(f"Building packages: {[p.name for p in target_packages]}")

    for pkg in target_packages:
        pkg_dist = build_package(pkg)

        # 复制构建产物到根 dist 目录
        for artifact in pkg_dist.glob("*"):
            shutil.copy2(artifact, dist_dir)

    print(f"\nBuild completed. Artifacts collected in {dist_dir}")
    if not args.packages:
        print("You can now upload to PyPI using: uv publish dist/*")


if __name__ == "__main__":
    main()
