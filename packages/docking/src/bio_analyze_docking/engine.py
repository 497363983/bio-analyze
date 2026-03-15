"""
zh: 对接引擎兼容性模块。
en: Docking engine compatibility module.

zh: 提供向后兼容的 DockingEngine 别名（映射到 VinaEngine）。
en: Provides backward compatible DockingEngine alias (mapped to VinaEngine).
"""

from .engines.vina import VinaEngine as DockingEngine

__all__ = ["DockingEngine"]
