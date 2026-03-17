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
from pytest_regressions.image_regression import ImageRegressionError



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
    if isinstance(call.excinfo.value, ImageRegressionError):
        err = call.excinfo.value
        attach_files = [
            ("Baseline image", err.expected_filename),
            ("Actual image", err.actual_filename),
            ("Pixel difference image", err.diff_filename),
        ]
        # 循环附加到Allure报告中
        for attach_name, file_path in attach_files:
            try:
                with open(file_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=attach_name,
                        attachment_type=allure.attachment_type.PNG
                    )
            except FileNotFoundError:
                continue
