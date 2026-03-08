from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import matplotlib.pyplot as plt
import seaborn as sns


import json
from pathlib import Path
import importlib.util

@dataclass
class PlotTheme:
    """SCI 风格绘图配置。"""
    
    name: str
    context: str = "paper"  # paper, notebook, talk, poster
    style: str = "ticks"    # darkgrid, whitegrid, dark, white, ticks
    palette: str = "deep"
    font: str = "sans-serif"
    font_scale: float = 1.0
    rc_params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: Path | str) -> PlotTheme:
        """从 JSON 文件加载主题配置。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 允许简单的 JSON 结构，并提供默认值
        return cls(
            name=data.get("name", Path(path).stem),
            context=data.get("context", "paper"),
            style=data.get("style", "ticks"),
            palette=data.get("palette", "deep"),
            font=data.get("font", "sans-serif"),
            font_scale=data.get("font_scale", 1.0),
            rc_params=data.get("rc_params", {})
        )

    def apply(self) -> None:
        """应用主题设置到 matplotlib/seaborn。"""
        # 默认启用 mathtext 支持 (不依赖外部 latex 编译器，使用 matplotlib 内置引擎)
        # 如果需要完整 LaTeX 支持，需要安装 TeX 发行版并设置 text.usetex = True
        # 这里使用 mathtext.fontset = 'stix' 或 'cm' 来获得类似 LaTeX 的效果
        default_rc = {
            "mathtext.fontset": "cm", # Computer Modern (类似 LaTeX 默认)
            # "text.usetex": False, # 默认关闭以避免依赖，matplotlib 的 mathtext 足够处理大多数公式
        }
        
        # 合并默认配置
        final_rc = default_rc.copy()
        final_rc.update(self.rc_params)
        
        sns.set_theme(
            context=self.context,
            style=self.style,
            palette=self.palette,
            font=self.font,
            font_scale=self.font_scale,
            rc=final_rc
        )
        # 显式更新关键字体配置，防止 seaborn 覆盖列表
        if "font.sans-serif" in self.rc_params:
            plt.rcParams["font.sans-serif"] = self.rc_params["font.sans-serif"]
            # print(f"DEBUG: Updated font.sans-serif to: {plt.rcParams['font.sans-serif']}")
        if "font.serif" in self.rc_params:
            plt.rcParams["font.serif"] = self.rc_params["font.serif"]
        if "axes.unicode_minus" in self.rc_params:
            plt.rcParams["axes.unicode_minus"] = self.rc_params["axes.unicode_minus"]
        
        # 确保 mathtext 配置生效
        if "mathtext.fontset" in final_rc:
            plt.rcParams["mathtext.fontset"] = final_rc["mathtext.fontset"]


# 常见的支持中文的字体列表
CHINESE_SANS_FONTS = [
    "Arial Unicode MS", # 优先尝试全能字体
    "Arial",
    "Helvetica",
    "DejaVu Sans",
    "SimHei",
    "Microsoft YaHei",
    "PingFang SC",
    "Heiti TC",
    "WenQuanYi Micro Hei",
    "sans-serif"
]

CHINESE_SERIF_FONTS = [
    "Times New Roman",
    "SimSun",
    "Songti SC",
    "serif"
]

# 预定义主题
THEMES = {
    "default": PlotTheme(
        name="default",
        rc_params={
            "font.sans-serif": CHINESE_SANS_FONTS,
            "axes.unicode_minus": False,  # 解决负号显示问题
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    ),
    "nature": PlotTheme(
        name="nature",
        font="sans-serif",
        font_scale=1.0,
        rc_params={
            "font.family": "sans-serif",
            "font.sans-serif": CHINESE_SANS_FONTS,
            "axes.unicode_minus": False,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "axes.linewidth": 0.5,
            "grid.linewidth": 0.5,
            "lines.linewidth": 1.0,
            "lines.markersize": 3,
            "patch.linewidth": 0.5,
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "xtick.minor.width": 0.4,
            "ytick.minor.width": 0.4,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.figsize": (3.5, 3.5), # 单栏宽度近似值
            "figure.dpi": 300,
        }
    ),
    "science": PlotTheme(
        name="science",
        rc_params={
            "font.family": "serif", # Science 有时偏好衬线字体
            "font.serif": CHINESE_SERIF_FONTS,
            "axes.unicode_minus": False,
            "axes.spines.top": True,
            "axes.spines.right": True, # 边框完整
            "xtick.direction": "in",
            "ytick.direction": "in",
        }
    )
}


def load_custom_theme(path_or_module: str) -> PlotTheme | None:
    """
    加载自定义主题。
    支持路径：
    1. .json 文件
    2. Python 模块路径 (例如 'my_package.my_theme')
    3. Python 文件路径 (例如 'path/to/my_theme.py')
    """
    path = Path(path_or_module)
    
    # 1. JSON 文件
    if path.suffix.lower() == ".json" and path.exists():
        try:
            return PlotTheme.from_json(path)
        except Exception as e:
            print(f"Failed to load theme from JSON {path}: {e}")
            return None

    # 2. Python 文件 (.py)
    if path.suffix.lower() == ".py" and path.exists():
        try:
            spec = importlib.util.spec_from_file_location("custom_theme_module", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # 查找 module 中的 PlotTheme 实例或 THEME 变量
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, PlotTheme):
                        return attr
                print(f"No PlotTheme instance found in {path}")
        except Exception as e:
            print(f"Failed to load theme from Python file {path}: {e}")
            return None

    # 3. Python 模块 (import string)
    try:
        module = importlib.import_module(path_or_module)
        # 查找 THEME 变量或任何 PlotTheme 实例
        if hasattr(module, "THEME") and isinstance(module.THEME, PlotTheme):
            return module.THEME
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, PlotTheme):
                return attr
    except ImportError:
        pass
    except Exception as e:
        print(f"Failed to import theme module {path_or_module}: {e}")

    return None


def set_theme(name: str = "default") -> None:
    """
    设置全局绘图主题。
    name 可以是预定义主题名称，也可以是自定义主题的路径/模块名。
    """
    # 1. 尝试预定义主题
    if name in THEMES:
        THEMES[name].apply()
        return

    # 2. 尝试加载自定义主题
    custom_theme = load_custom_theme(name)
    if custom_theme:
        custom_theme.apply()
        return

    # 3. 回退
    print(f"Theme '{name}' not found. Falling back to default.")
    THEMES["default"].apply()
