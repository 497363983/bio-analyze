"""RNA-Seq quantification module with pluggable backends."""

from .engines import (
    FeatureCountsQuantifier,
    HTSeqCountQuantifier,
    KallistoQuantifier,
    RSEMQuantifier,
    SalmonQuantifier,
)
from .framework import (
    DEFAULT_PARAMETER_TEMPLATES,
    DEFAULT_QUANT_TOOL,
    BaseQuantifier,
    QuantifierRegistry,
    QuantManager,
    QuantRunResult,
    QuantToolSpec,
    compare_quant_results,
    discover_alignment_bams,
    get_quantifier_required_tools,
    get_quantifier_specs,
    list_available_quantifiers,
    register_quantifier,
)

__all__ = [
    "DEFAULT_PARAMETER_TEMPLATES",
    "DEFAULT_QUANT_TOOL",
    "BaseQuantifier",
    "FeatureCountsQuantifier",
    "HTSeqCountQuantifier",
    "KallistoQuantifier",
    "QuantManager",
    "QuantRunResult",
    "QuantToolSpec",
    "QuantifierRegistry",
    "RSEMQuantifier",
    "SalmonQuantifier",
    "compare_quant_results",
    "discover_alignment_bams",
    "get_quantifier_required_tools",
    "get_quantifier_specs",
    "list_available_quantifiers",
    "register_quantifier",
]
