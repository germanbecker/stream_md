"""
Base classes and utilities for token processing in the streaming markdown parser.
"""

from __future__ import annotations

from typing import ClassVar, Literal, Optional, Union, List
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from rich.style import StyleStack, Style
import logging

from stream_md.type_defs import (
    STREAM_ELEMENT_POP,
    RuleResults, 
    StreamElement, 
    PreProcessOutput, 
    ProcessOutput, 
    ConsumeResults
)

logger = logging.getLogger(__name__)

DEFAULT_CONTAINER = "_default_container"


class TokenStack:
    """Stack for managing nested tokens during parsing."""
    
    def __init__(self):
        self.tokens: List[Token] = []
    
    def push(self, token: Token) -> None:
        """Push a token onto the stack."""
        self.tokens.append(token)

    def pop(self, token: Optional[Token] = None) -> Token:
        """Pop a token from the stack."""
        if token is None:
            return self.tokens.pop()
        else:
            for i, t in enumerate(self.tokens):
                if t is token:
                    return self.tokens.pop(i)
        raise KeyError(f"Token {token} not found in the stack")

    def token_at(self, position: int) -> Token:
        """Get token at specific position."""
        return self.tokens[position]
    
    @property
    def top(self) -> Token:
        """Get the top token from the stack."""
        return self.tokens[-1]

    def next(self, token: Token) -> Optional[Token]:
        """Get the next token after the given token."""
        for i in range(len(self.tokens) - 1):
            if self.tokens[i] is token:
                return self.tokens[i + 1]
        return None
    
    def get_all_previous(self, position: int) -> List[Token]:
        """Get all tokens before the given position."""
        return self.tokens[:position]

    def remove_at(self, position: int) -> Token:
        """Remove and return token at specific position."""
        return self.tokens.pop(position)

    def __repr__(self):
        return "->".join([str(type(x)) for x in self.tokens])


def default_token_stack() -> TokenStack:
    """Create a default token stack."""
    return TokenStack()


def default_style_stack() -> StyleStack:
    """Create a default style stack."""
    return StyleStack(Style(color="orange1"))


@dataclass
class MarkdownContainer:
    """Container for shared parsing state."""
    style_stack: StyleStack = field(default_factory=default_style_stack)
    token_stack: TokenStack = field(default_factory=default_token_stack)

    _instances: ClassVar[dict[str, 'MarkdownContainer']] = {}

    @classmethod
    def initialize(cls, cid:str = DEFAULT_CONTAINER) -> None:
        """Initialize the global container instance."""
        cls._instances[cid] = cls()

    @classmethod
    def get(cls, cid= DEFAULT_CONTAINER) -> 'MarkdownContainer':
        """Get the global container instance."""
        if cid not in cls._instances:
            raise RuntimeError("Container not initialized")
        return cls._instances[cid]


@dataclass(frozen=True)
class FoundChild:
    """Represents a found child token."""
    token: Token
    position: int
    is_match: Literal[RuleResults.MATCH] = RuleResults.MATCH


@dataclass(frozen=True)
class NoChild:
    """Represents no child token found."""
    is_match: Literal[RuleResults.NO_MATCH] = RuleResults.NO_MATCH


@dataclass(frozen=True)
class PossibleChild:
    """
    Represents a possible child token.
    
    There are at least one possible tokens present, position is the nearest 
    position of potential start. This means anything before position is 
    guaranteed to not belong to child token.
    """
    position: int 
    is_match: Literal[RuleResults.POSSIBLE] = RuleResults.POSSIBLE


FindChild = Union[FoundChild, NoChild, PossibleChild]


class Token(ABC):
    """
    Base class for token processing.
    
    General logic:
    <input(str)> --> preprocess -> <str> -> next_token -> <ProcessOutput> -> postprocess -> <ProcessOutput>
    """

    "add a syle pop before poping self"
    add_a_pop: bool = False

    def __init__(self, cid = DEFAULT_CONTAINER):
        self.cid = cid
        self.inner: List[StreamElement] = []
        self.outer = ""
        self.delta: List[StreamElement] = []
        self.before_new_token = ""
        self.stack = MarkdownContainer.get(self.cid).token_stack
        self.style_stack = MarkdownContainer.get(self.cid).style_stack
        self.done = False
        self.stack.push(self)

    def preprocess(self, input_text: str, end_stream: bool = False) -> PreProcessOutput:
        """
        Process input before further processing by downstream tokens.
        
        In particular, it should detect exit and filter out input after the exit.

        Args:
            input_text: The input string to be processed
            end_stream: Whether this is the end of the stream
            
        Returns:
            PreProcessOutput containing:
                - processed: The input for the rest of the processing
                - remaining: Part of the original input that hasn't been processed
                - done: Whether processing is complete
        """
        return PreProcessOutput(processed=input_text, remaining="", done=False)

    def postprocess(self, input_data: ProcessOutput, end_stream: bool = False) -> ProcessOutput:
        """
        Do post processing after (possible) downstream tokens.
        
        Args:
            input_data: The output of the previous stage
            end_stream: Whether this is the end of the stream
            
        Returns:
            ProcessOutput: The postprocessed data
        """
        self.delta = []
        return input_data

    @abstractmethod
    def find_child(self, input_text: str, end_stream: bool = False) -> FindChild:
        """
        Find new child token. If found, stack should be updated.
        
        Args:
            input_text: Input text to search for child tokens
            end_stream: Whether this is the end of the stream
            
        Returns:
            FindChild result indicating if a child was found
        """
        raise NotImplementedError()

    @abstractmethod
    def consume(self, input_text: str, end_stream: bool = False) -> ConsumeResults:
        """
        Consume input and return ConsumeResults.
        
        This is only called when the token is the top of the stack.
        
        Args:
            input_text: Input text to consume
            end_stream: Whether this is the end of the stream
            
        Returns:
            ConsumeResults with processed elements and remaining text
        """
        raise NotImplementedError()

    def flush(self) -> List[StreamElement]:
        """
        Force finishing processing, because parent says so.
        
        This shouldn't happen under normal circumstances.
        
        Returns:
            List of remaining stream elements
        """
        logger.warning(f"Flushing token {self}")
        if next_token := self.stack.next(self):
            self.inner.extend(next_token.flush())
        self.stack.pop(self)
        return self.inner

    @property
    def is_last_token(self) -> bool:
        """Check if this is the last token in the stack."""
        return self.stack.top is self

    def process(self, input_text: str, end_stream: bool = False) -> ProcessOutput:
        """
        Main processing method that orchestrates the parsing pipeline.
        
        Args:
            input_text: Input text to process
            end_stream: Whether this is the end of the stream
            
        Returns:
            ProcessOutput with stream elements and remaining text
        """
        preresults = self.preprocess(input_text, end_stream)
        end_stream = end_stream and not preresults.remaining 
        next_token = self.stack.next(self)

        if next_token:
            # Process downstream token
            downstream = next_token.process(
                preresults.processed, 
                end_stream or preresults.done
            )
        else:
            # First try to find a child
            child_result = self.find_child(preresults.processed, end_stream or preresults.done)
            
            if child_result.is_match != RuleResults.NO_MATCH:
                # If there is a (potential) new child, only consume until the position
                before = preresults.processed[:child_result.position]
                after = preresults.processed[child_result.position:]
            else:
                before = preresults.processed
                after = ""
                
            result = self.consume(before, end_stream and not after)
            
            # Handle child token processing
            if child_result.is_match == RuleResults.MATCH:
                next_result = child_result.token.process(after, end_stream or preresults.done)
                downstream = ProcessOutput(
                    stream=result.inner + next_result.stream,
                    remaining=result.remaining + next_result.remaining
                )
            else:
                downstream = ProcessOutput(
                    stream=result.inner, 
                    remaining=result.remaining + after
                )
                
            if preresults.done and not downstream.remaining:
                if next_token := self.stack.next(self):
                    # This shouldn't happen
                    flushed = next_token.flush()
                    downstream = ProcessOutput(
                        stream=flushed + downstream.stream, 
                        remaining=downstream.remaining
                    )
                # Remove ourselves from the stack
                if self.add_a_pop:
                    downstream.stream.append(STREAM_ELEMENT_POP)
                self.stack.pop(self)

        postprocess_result = self.postprocess(downstream, end_stream)
        self.inner += postprocess_result.stream
        postprocess_result.remaining += preresults.remaining
        consumed_length = len(input_text) - len(postprocess_result.remaining)
        self.outer += input_text[:consumed_length]
        return postprocess_result

    @classmethod
    @abstractmethod
    def rule(cls, s: str, end_stream: bool = False, cid:str = DEFAULT_CONTAINER) -> 'RuleResult':
        """
        Class method to check if this token type matches the input.
        
        Args:
            s: Input string to check
            end_stream: Whether this is the end of the stream
            
        Returns:
            RuleResult indicating match status
        """
        raise NotImplementedError


@dataclass(frozen=True)
class Match:
    """Represents a successful rule match."""
    token: Token
    position: int
    result: Literal[RuleResults.MATCH] = RuleResults.MATCH


@dataclass(frozen=True)
class Possible:
    """Represents a possible rule match."""
    position: int
    result: Literal[RuleResults.POSSIBLE] = RuleResults.POSSIBLE


@dataclass
class NoMatch:
    """Represents no rule match."""
    result: Literal[RuleResults.NO_MATCH] = RuleResults.NO_MATCH


RuleResult = Union[Match, Possible, NoMatch]
