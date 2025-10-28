"""
Main MarkDownRender class for streaming markdown parsing and rendering.
"""

import logging
from typing import List

from rich.console import Console
from rich.style import Style, StyleStack

from stream_md.tokens.base import MarkdownContainer
from stream_md.tokens.block.container.root import Root
from stream_md.type_defs import StreamElement

logger = logging.getLogger(__name__)


class MarkDownRender:
    """
    A streaming markdown parser and renderer using Python Rich.
    
    This class processes markdown content incrementally, making it perfect
    for real-time applications like chat interfaces or streaming APIs.
    
    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> renderer = MarkDownRender(console)
        >>> renderer.stream_parse("# Hello **World**")
        >>> renderer.end_stream()
    """
    
    def __init__(self, console: Console):
        """
        Initialize the markdown renderer.
        
        Args:
            console: A Rich Console instance for output rendering
        """
        self.buffer = ""
        MarkdownContainer.initialize()
        self.root = Root()
        self.console = console
        self.style_stack = StyleStack(Style(color="misty_rose3"))

    def render(self, stream: List[StreamElement]) -> None:
        """
        Render a stream of elements to the console.
        
        Args:
            stream: List of StreamElement objects to render
        """
        for element in stream:
            if element.element_type == "style_stack":
                if element.element.action == "pop":
                    self.style_stack.pop()
                else:
                    self.style_stack.push(element.element.style)  
            else:
                self.console.print(
                    element.element, 
                    end="", 
                    style=sum(self.style_stack._stack, Style())
                )

    def stream_parse(self, s: str) -> None:
        """
        Parse a chunk of markdown text and render it.
        
        This method can be called multiple times with different chunks
        of markdown content. The parser maintains state between calls.
        
        Args:
            s: A string chunk of markdown content to parse
        """
        remaining = self.buffer + s

        while True:
            output = self.root.process(remaining)
            self.render(output.stream)
            
            if not output.remaining or output.remaining == remaining:
                break
                
            remaining = output.remaining
            
        self.buffer = output.remaining

    def end_stream(self) -> None:
        """
        Signal the end of the markdown stream and flush any remaining content.
        
        This method should be called when no more markdown content will be
        provided to ensure all content is properly rendered.
        """
        remaining = self.buffer
        
        while True:
            output = self.root.process(remaining, end_stream=True)
            self.render(output.stream)
            
            if not output.remaining or output.remaining == remaining:
                break
                
            remaining = output.remaining
            
        if output.remaining:
            logger.warning(f"Remaining content after end_stream: {output.remaining!r}")