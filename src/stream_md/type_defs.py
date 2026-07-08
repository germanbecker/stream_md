"""
Type definitions and data structures for the streaming markdown parser.
"""

from dataclasses import dataclass
from typing import Literal, Union, List
from enum import Enum

from rich.style import Style
from rich.console import RenderableType


@dataclass
class StackStylePop:
    """Represents a style stack pop operation."""
    action: Literal["pop"] = "pop"


@dataclass
class StackStylePush:
    """Represents a style stack push operation."""
    style: Style
    action: Literal["push"] = "push"


StackStyleAction = Union[StackStylePop, StackStylePush]


@dataclass
class StreamElementPrintable:
    """A printable element in the stream."""
    element: Union[str, RenderableType]
    element_type: Literal["printable"] = "printable"


@dataclass
class StreamElementSyleStack:
    """A style stack operation element in the stream."""
    element: StackStyleAction
    element_type: Literal["style_stack"] = "style_stack"


StreamElement = Union[StreamElementPrintable, StreamElementSyleStack]

# Commonly used stream elements (keeping original typos for compatibility)
NULL_STREM_ELEMENT = StreamElementPrintable("")
STREAM_ELEMT_POP = StreamElementSyleStack(StackStylePop())

# Correctly spelled versions for new code
NULL_STREAM_ELEMENT = StreamElementPrintable("")
STREAM_ELEMENT_POP = StreamElementSyleStack(StackStylePop())


class RuleResults(Enum):
    """Results from rule matching operations."""
    MATCH = "match"
    NO_MATCH = "no_match"
    POSSIBLE = "possible"


@dataclass
class ProcessOutput:
    """Output from processing markdown text."""
    stream: List[StreamElement]
    remaining: str


@dataclass(frozen=True)
class PreProcessOutput:
    """Results from preprocessing markdown text."""
    processed: str
    remaining: str
    done: bool


@dataclass
class ConsumeResults:
    """Results from consuming markdown text."""
    inner: List[StreamElement]
    """The processed stream elements"""
    remaining: str
    """Unconsumed text that should be processed next"""


class State:
    """Base class for parser state."""
    pass
