"""
Stream MD - A streaming markdown parser and formatter for Python Rich.

This package provides real-time markdown parsing and rendering capabilities,
perfect for chat applications, streaming APIs, or progressive content loading.
"""

from .markdown import MarkDownRender
from .type_defs import (
    StreamElement,
    StreamElementPrintable,
    StreamElementSyleStack,
    StackStyleAction,
    StackStylePop,
    StackStylePush,
    ProcessOutput,
    ConsumeResults,
    RuleResults,
)

__version__ = "0.1.0"
__author__ = "German Becker"
__email__ = "german.becker@gmail.com"

__all__ = [
    "MarkDownRender",
    "StreamElement",
    "StreamElementPrintable", 
    "StreamElementSyleStack",
    "StackStyleAction",
    "StackStylePop",
    "StackStylePush",
    "ProcessOutput",
    "ConsumeResults",
    "RuleResults",
]
