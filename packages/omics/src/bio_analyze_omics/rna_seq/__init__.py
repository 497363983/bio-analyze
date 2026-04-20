"""Transcriptomics analysis pipeline package."""

# pylint: disable=undefined-variable,import-outside-toplevel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import RNASeqPipeline as RNASeqPipeline


def __getattr__(name: str):
    if name == "RNASeqPipeline":
        from .pipeline import RNASeqPipeline

        return RNASeqPipeline
    raise AttributeError(name)
