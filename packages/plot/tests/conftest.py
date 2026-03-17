import matplotlib

# Set backend to Agg before importing pyplot to avoid GUI dependencies
matplotlib.use("Agg")

import io
import random
import numpy as np
import pytest
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from bio_analyze_plot import theme



@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Automatically setup the test environment for all tests.
    - Seeds random number generators for determinism.
    - Patches theme fonts to ensure consistent rendering across platforms.
    """
    # Seed RNGs
    np.random.seed(42)
    random.seed(42)

    # Patch fonts to ensure consistency across environments (e.g., CI vs Local)
    # DejaVu Sans is standard in Matplotlib
    monkeypatch.setattr(theme, "CHINESE_SANS_FONTS", ["DejaVu Sans"])
    monkeypatch.setattr(theme, "CHINESE_SERIF_FONTS", ["DejaVu Serif"])


@pytest.fixture
def check_plot(image_regression):
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
            # Use bbox_inches="tight" to match typical save_plot behavior
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
            buf.seek(0)
            image_regression.check(buf.getvalue(), diff_threshold=0.1)
        plt.close(fig)

    return _check

@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(node, call, report):
    """捕获图像回归失败，自动附加差异图到 Allure (兼容所有 pytest-regressions 版本)"""
    excinfo = call.excinfo
    if not excinfo:
        return

    # 稳健判断：不依赖导入，直接检查异常类名
    exc_type_name = excinfo.typename
    if "ImageRegressionError" in exc_type_name:
        err = excinfo.value
        
        # 尝试从异常对象中获取图片路径 (兼容不同版本的属性名)
        # 常见属性名: expected_filename / actual_filename / diff_filename
        attachments = []
        
        # 尝试获取预期图
        if hasattr(err, "expected_filename"):
            attachments.append(("1. Baseline image", err.expected_filename))
        elif hasattr(err, "expected"):
            attachments.append(("1. Baseline image", err.expected))
            
        # 尝试获取实际图
        if hasattr(err, "actual_filename"):
            attachments.append(("2. Actual image", err.actual_filename))
        elif hasattr(err, "actual"):
            attachments.append(("2. Actual image", err.actual))
            
        # 尝试获取差异图
        if hasattr(err, "diff_filename"):
            attachments.append(("3. Pixel difference image", err.diff_filename))
        elif hasattr(err, "diff"):
            attachments.append(("3. Pixel difference image", err.diff))

        # 执行附加
        for name, file_path in attachments:
            try:
                with open(file_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=name,
                        attachment_type=allure.attachment_type.PNG
                    )
            except (FileNotFoundError, TypeError):
                continue
