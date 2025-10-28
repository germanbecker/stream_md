"""
Tests for the main MarkDownRender class.
"""

import pytest
from io import StringIO
from rich.console import Console

from stream_md import MarkDownRender


class TestMarkDownRender:
    """Test cases for MarkDownRender class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.output = StringIO()
        self.console = Console(file=self.output, width=80, legacy_windows=False)
        self.renderer = MarkDownRender(self.console)
    
    def test_initialization(self):
        """Test that MarkDownRender initializes correctly."""
        assert self.renderer.buffer == ""
        assert self.renderer.console is self.console
        assert self.renderer.root is not None
        assert self.renderer.style_stack is not None
    
    def test_simple_text(self):
        """Test rendering simple text."""
        self.renderer.stream_parse("Hello, World!")
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "Hello, World!" in output
    
    def test_bold_text(self):
        """Test rendering bold text."""
        self.renderer.stream_parse("This is **bold** text")
        self.renderer.end_stream()
        
        # The exact output will depend on the implementation
        # but we can check that the text was processed
        output = self.output.getvalue()
        assert "bold" in output
    
    def test_italic_text(self):
        """Test rendering italic text."""
        self.renderer.stream_parse("This is *italic* text")
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "italic" in output
    
    def test_heading(self):
        """Test rendering headings."""
        self.renderer.stream_parse("# Main Heading")
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "Main Heading" in output
    
    def test_streaming_chunks(self):
        """Test that content can be streamed in chunks."""
        chunks = ["# Hello ", "**World**\n\n", "This is ", "*streaming*!"]
        
        for chunk in chunks:
            self.renderer.stream_parse(chunk)
        
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "Hello" in output
        assert "World" in output
        assert "streaming" in output
    
    def test_code_block(self):
        """Test rendering code blocks."""
        code = "```python\nprint('Hello, World!')\n```"
        self.renderer.stream_parse(code)
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "print" in output
    
    def test_empty_input(self):
        """Test handling empty input."""
        self.renderer.stream_parse("")
        self.renderer.end_stream()
        
        # Should not raise any exceptions
        output = self.output.getvalue()
        # Empty input should produce minimal output
    
    def test_multiple_end_stream_calls(self):
        """Test that multiple end_stream calls don't cause issues."""
        self.renderer.stream_parse("Hello")
        self.renderer.end_stream()
        self.renderer.end_stream()  # Should not cause issues
        
        output = self.output.getvalue()
        assert "Hello" in output


class TestStreamingBehavior:
    """Test streaming behavior with various chunk sizes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.output = StringIO()
        self.console = Console(file=self.output, width=80, legacy_windows=False)
        self.renderer = MarkDownRender(self.console)
    
    def test_random_chunk_sizes(self):
        """Test with random chunk sizes to simulate real streaming."""
        import random
        
        markdown = """# Test Document

This is a **test** document with *various* formatting.

## Subsection

Here's some code:

```python
def hello():
    print("Hello, World!")
```

And some more text.
"""
        
        # Split into random chunks
        chunks = []
        i = 0
        while i < len(markdown):
            chunk_size = random.randint(1, 20)
            chunk = markdown[i:i + chunk_size]
            chunks.append(chunk)
            i += chunk_size
        
        # Process chunks
        for chunk in chunks:
            self.renderer.stream_parse(chunk)
        
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "Test Document" in output
        assert "test" in output
        assert "various" in output
        assert "Subsection" in output
        assert "hello" in output
    
    def test_single_character_chunks(self):
        """Test with single character chunks."""
        text = "# Hello **World**"
        
        for char in text:
            self.renderer.stream_parse(char)
        
        self.renderer.end_stream()
        
        output = self.output.getvalue()
        assert "Hello" in output
        assert "World" in output