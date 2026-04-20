import matplotlib

# Set backend to Agg before importing pyplot to avoid GUI dependencies
matplotlib.use("Agg")

import io
import logging
import os
import pathlib

import allure
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure
from PIL import Image

SNAPSHOT_DIR_NAME = "snapshot"

def _get_module_snapshot_datadir(request: pytest.FixtureRequest) -> pathlib.Path:

    test_file_path = pathlib.Path(request.fspath)
    test_module_dir = test_file_path.parent
    test_file_name = test_file_path.stem
    test_func_name = request.node.name

    snapshot_datadir = test_module_dir / SNAPSHOT_DIR_NAME / test_file_name / test_func_name
    snapshot_datadir.mkdir(parents=True, exist_ok=True)

    return snapshot_datadir

@pytest.fixture
def lazy_datadir(request: pytest.FixtureRequest) -> pathlib.Path:
    """
    pytest-regressions 所有fixture的路径根源，官方推荐的全局自定义入口
    最终路径规则：[当前模块tests目录]/[SNAPSHOT_DIR_NAME]/[测试文件名]/[测试函数名]
    """
    # 动态获取当前执行的测试文件绝对路径（自动适配monorepo不同模块）
    test_file_path = pathlib.Path(request.fspath)
    # 当前测试文件所在的模块tests目录
    test_module_dir = test_file_path.parent
    # 测试文件名（不含后缀，如test_scatter）
    test_file_stem = test_file_path.stem
    # 测试函数名（如test_scatter_complex）
    test_case_name = request.node.name

    # 拼接最终目标路径
    target_datadir = test_module_dir / SNAPSHOT_DIR_NAME / test_file_stem / test_case_name
    # 自动创建目录，避免首次运行报错
    target_datadir.mkdir(parents=True, exist_ok=True)

    return target_datadir

@pytest.fixture
def original_datadir(lazy_datadir: pathlib.Path) -> pathlib.Path:
    """和lazy_datadir保持一致，确保基准文件的读写都在同一目录"""
    return lazy_datadir

def pytest_configure(config):
    reg_logger = logging.getLogger("pytest_regressions")
    reg_logger.setLevel(logging.DEBUG)
    reg_logger.addHandler(logging.StreamHandler())

@pytest.fixture
def check_plot(request, image_regression):
    """
    Helper fixture to check a matplotlib Figure against a baseline image.
    Usage:
        def test_my_plot(check_plot):
            fig = ...
            check_plot(fig)
    """

    def _check(fig, dpi=100):
        if not isinstance(fig, Figure):
            raise ValueError("check_plot expects a matplotlib.figure.Figure object")

        with io.BytesIO() as buf:
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
            buf.seek(0)
            img_bytes = buf.getvalue()

            test_file_path = pathlib.Path(request.node.fspath)
            test_module_dir = test_file_path.parent
            test_file_stem = test_file_path.stem
            test_case_name = request.node.name
            expected_dir = test_module_dir / SNAPSHOT_DIR_NAME / test_file_stem / test_case_name
            expected_dir.mkdir(parents=True, exist_ok=True)
            expected_path = expected_dir / f"{test_case_name}.png"
            output_dir = test_module_dir / "output" / test_file_stem / test_case_name
            output_dir.mkdir(parents=True, exist_ok=True)

            if request.config.getoption("force_regen"):
                expected_path.write_bytes(img_bytes)
                obtained_path = output_dir / f"{test_case_name}.obtained.png"
                obtained_path.write_bytes(img_bytes)
                diff_path = output_dir / f"{test_case_name}.obtained_diff.png"
                if diff_path.exists():
                    diff_path.unlink()
                plt.close(fig)
                return

            image_regression.datadir = output_dir

            try:
                image_regression.check(
                    img_bytes,
                    diff_threshold=5,
                    fullpath=str(expected_path)
                )
            except AssertionError as e:
                msg = str(e)
                lines = msg.split('\n')

                if len(lines) < 3 or "Difference between images too high" not in lines[0]:
                    raise e

                expected_path = lines[1].strip()
                actual_path = lines[2].strip()

                if not (os.path.exists(expected_path) and os.path.exists(actual_path)):
                    raise e

                actual_path = str(pathlib.Path(actual_path))

                print("\n" + "=" * 60)
                print("【Image regression failure】")
                print(f"Baseline image path: {expected_path}")
                print(f"Actual image path: {actual_path}")

                expected_img = Image.open(expected_path).convert("RGB")
                actual_img = Image.open(actual_path).convert("RGB").resize(expected_img.size)
                expected_arr = np.array(expected_img)
                actual_arr = np.array(actual_img)
                diff_mask = np.any(np.abs(expected_arr.astype(int) - actual_arr.astype(int)) > 0, axis=-1)
                diff_arr = (actual_arr * 0.5).astype(np.uint8)
                diff_arr[diff_mask] = [255, 0, 0]
                diff_img = Image.fromarray(diff_arr)
                diff_path = f"{os.path.splitext(actual_path)[0]}_diff.png"
                diff_img.save(diff_path)

                diff_pixels = np.sum(diff_mask)
                print(f"Diff image path: {diff_path}")
                print(f"Diff pixels: {diff_pixels}")
                print("=" * 60 + "\n")

                try:
                    allure.attach.file(
                        expected_path,
                        name=f"Expected - {os.path.basename(expected_path)}",
                        attachment_type=allure.attachment_type.PNG
                    )
                    allure.attach.file(
                        actual_path,
                        name=f"Actual - {os.path.basename(actual_path)}",
                        attachment_type=allure.attachment_type.PNG
                    )
                    allure.attach.file(
                        diff_path,
                        name=f"Diff - {os.path.basename(diff_path)}",
                        attachment_type=allure.attachment_type.PNG
                    )
                    print("[Allure Attach] Successfully attached Expected, Actual, and Diff images.")
                except Exception as err:
                    print(f"[Allure Attach] Failed to attach images: {err}")

                raise e
            finally:
                plt.close(fig)

    return _check
