import matplotlib

# Set backend to Agg before importing pyplot to avoid GUI dependencies
matplotlib.use("Agg")

import os
import io
import random
import numpy as np
import pytest
import logging
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.figure import Figure
from bio_analyze_plot import theme
import allure
from pytest_regressions.image_regression import ImageRegressionFixture

# ========== 新增：调低日志级别，打印pytest-regressions路径 ==========
def pytest_configure(config):
    reg_logger = logging.getLogger("pytest_regressions")
    reg_logger.setLevel(logging.DEBUG)
    reg_logger.addHandler(logging.StreamHandler())

# ========== 原有逻辑：保留不动 ==========
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

# ========== 核心修改：重写check_plot fixture，自动生成差异图 ==========
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
            img_bytes = buf.getvalue()
            
            try:
                # 原有对比逻辑
                image_regression.check(img_bytes, diff_threshold=0.1)
            except AssertionError as e:
                # ========== 新增：对比失败时生成差异图 ==========
                # 1. 提取基准图/实际图路径（从image_regression fixture中获取）
                expected_path = image_regression.expected_filename
                actual_path = image_regression.actual_filename
                
                # 2. 打印路径到控制台
                print("\n" + "="*60)
                print(f"【图像回归失败】")
                print(f"基准图路径: {expected_path}")
                print(f"实际图路径: {actual_path}")
                
                # 3. 生成并保存差异图
                if os.path.exists(expected_path) and os.path.exists(actual_path):
                    # 读取图片并统一尺寸
                    expected_img = Image.open(expected_path).convert("RGB")
                    actual_img = Image.open(actual_path).convert("RGB").resize(expected_img.size)
                    
                    # 计算像素差异
                    expected_arr = np.array(expected_img)
                    actual_arr = np.array(actual_img)
                    diff_arr = np.where(np.abs(expected_arr - actual_arr) > 0, [255,0,0], [255,255,255])
                    diff_img = Image.fromarray(diff_arr.astype(np.uint8))
                    
                    # 保存差异图（路径=实际图+_diff）
                    diff_path = f"{os.path.splitext(actual_path)[0]}_diff.png"
                    diff_img.save(diff_path)
                    
                    # 打印差异图路径和差异像素数
                    diff_pixels = np.sum(np.abs(expected_arr - actual_arr) > 0)
                    print(f"差异图路径: {diff_path}")
                    print(f"差异像素数: {diff_pixels}")
                print("="*60 + "\n")
                
                # 重新抛出异常，保持测试失败状态
                raise e
            
            finally:
                plt.close(fig)

    return _check

# ========== 原有逻辑：保留不动（仅优化扫描逻辑，支持子目录） ==========
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
        keywords = ["expected", "actual", "diff", "difference"]

        # ========== 优化：递归扫描子目录（解决图片在子文件夹的问题） ==========
        if os.path.exists(test_dir):
            # 递归遍历所有子目录
            for root, dirs, files in os.walk(test_dir):
                for filename in files:
                    # 1. 先判断是不是图片
                    if filename.lower().endswith(image_exts):
                        # 2. 再判断文件名是否相关
                        is_relevant = (
                            test_name in filename 
                            or any(kw in filename.lower() for kw in keywords)
                        )

                        if is_relevant:
                            file_path = os.path.join(root, filename)
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