"""
Docking engine compatibility module.

Provides backward compatible DockingEngine alias (mapped to VinaEngine).
"""

from .engines.vina import VinaEngine as DockingEngine

__all__ = ["DockingEngine"]
