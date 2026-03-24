import random
import numpy as np
import pytest
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

    monkeypatch.setattr(theme, "CHINESE_SANS_FONTS", ["DejaVu Sans"])
    monkeypatch.setattr(theme, "CHINESE_SERIF_FONTS", ["DejaVu Serif"])
