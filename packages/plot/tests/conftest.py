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

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    终极解决方案：
    1. 监听测试用例是否失败
    2. 如果失败，直接去测试目录下扫盘
    3. 把所有看起来像是差异图的文件都附加到 Allure
    """
    outcome = yield
    report = outcome.get_result()

    # 仅在测试执行阶段失败时触发
    if report.when == "call" and report.failed:
        # 获取当前测试文件所在的文件夹路径
        test_file_path = item.fspath
        test_dir = str(test_file_path.dirname)
        test_name = test_file_path.purebasename  # 测试文件名（不含.py）

        print(f"[Allure Attach] Test failed. Scanning for images in: {test_dir}")

        # 定义要扫描的图片后缀
        image_exts = (".png", ".jpg", ".jpeg")
        
        # 定义 pytest-regressions 常见的差异图命名关键词
        # 它通常会生成类似 test_name.expected.png, test_name.actual.png, test_name.diff.png
        keywords = ["expected", "actual", "diff", "difference"]

        # 开始遍历目录
        if os.path.exists(test_dir):
            for filename in os.listdir(test_dir):
                # 1. 先判断是不是图片
                if filename.lower().endswith(image_exts):
                    
                    # 2. 再判断文件名是否包含测试名或关键词 (避免把项目里无关的图也挂上去)
                    is_relevant = (
                        test_name in filename 
                        or any(kw in filename.lower() for kw in keywords)
                    )

                    if is_relevant:
                        file_path = os.path.join(test_dir, filename)
                        try:
                            with open(file_path, "rb") as f:
                                # 附加图片
                                allure.attach(
                                    f.read(),
                                    name=filename,
                                    attachment_type=allure.attachment_type.PNG
                                )
                            print(f"[Allure Attach] Success: {filename}")
                        except Exception as e:
                            print(f"[Allure Attach] Failed to attach {filename}: {e}")
