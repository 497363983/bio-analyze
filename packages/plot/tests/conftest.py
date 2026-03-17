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
                image_regression.check(img_bytes, diff_threshold=3)
            except AssertionError as e:
                # ========== 新增：对比失败时生成差异图 ==========
                # 解析 AssertionError 提取基准图和实际图的路径
                msg = str(e)
                lines = msg.split('\n')
                
                expected_path = None
                actual_path = None
                if len(lines) >= 3 and "Difference between images too high" in lines[0]:
                    expected_path = lines[1].strip()
                    actual_path = lines[2].strip()
                
                if expected_path and actual_path and os.path.exists(expected_path) and os.path.exists(actual_path):
                    # 2. 打印路径到控制台
                    print("\n" + "="*60)
                    print(f"【图像回归失败】")
                    print(f"基准图路径: {expected_path}")
                    print(f"实际图路径: {actual_path}")
                    
                    # 3. 生成并保存差异图
                    # 读取图片并统一尺寸
                    expected_img = Image.open(expected_path).convert("RGB")
                    actual_img = Image.open(actual_path).convert("RGB").resize(expected_img.size)
                    
                    # 计算像素差异
                    expected_arr = np.array(expected_img)
                    actual_arr = np.array(actual_img)
                    
                    # 生成红色高亮差异的图片，底层使用较浅的实际图片以便观察
                    diff_mask = np.any(np.abs(expected_arr.astype(int) - actual_arr.astype(int)) > 0, axis=-1)
                    diff_arr = (actual_arr * 0.5).astype(np.uint8)  # 调暗原图
                    diff_arr[diff_mask] = [255, 0, 0]  # 差异部分标红
                    diff_img = Image.fromarray(diff_arr)
                    
                    # 保存差异图（路径=实际图+_diff.png）
                    diff_path = f"{os.path.splitext(actual_path)[0]}_diff.png"
                    diff_img.save(diff_path)
                    
                    # 打印差异图路径和差异像素数
                    diff_pixels = np.sum(diff_mask)
                    print(f"差异图路径: {diff_path}")
                    print(f"差异像素数: {diff_pixels}")
                    print("="*60 + "\n")
                    
                    # 4. 附加图片到 Allure 报告
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
                
                # 重新抛出异常，保持测试失败状态
                raise e
            
            finally:
                plt.close(fig)

    return _check

# ========== 原有逻辑：保留不动（仅优化扫描逻辑，支持子目录） ==========
# (已移除，因为 check_plot 内部已经精确地附加了相关图片，避免报告中出现重复或无关图片)