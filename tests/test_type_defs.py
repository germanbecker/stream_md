"""
Tests for type definitions and data structures.
"""

import pytest
from rich.style import Style

from stream_md.type_defs import (
    StackStylePop,
    StackStylePush,
    StreamElementPrintable,
    StreamElementSyleStack,
    ProcessOutput,
    ConsumeResults,
    RuleResults,
    NULL_STREAM_ELEMENT,
    STREAM_ELEMENT_POP,
)


class TestStackStyleOperations:
    """Test stack style operations."""
    
    def test_stack_style_pop(self):
        """Test StackStylePop creation."""
        pop = StackStylePop()
        assert pop.action == "pop"
    
    def test_stack_style_push(self):
        """Test StackStylePush creation."""
        style = Style(color="red")
        push = StackStylePush(style=style)
        assert push.action == "push"
        assert push.style == style


class TestStreamElements:
    """Test stream element types."""
    
    def test_stream_element_printable(self):
        """Test StreamElementPrintable creation."""
        element = StreamElementPrintable("Hello")
        assert element.element == "Hello"
        assert element.element_type == "printable"
    
    def test_stream_element_style_stack(self):
        """Test StreamElementSyleStack creation."""
        pop = StackStylePop()
        element = StreamElementSyleStack(pop)
        assert element.element == pop
        assert element.element_type == "style_stack"
    
    def test_null_stream_element(self):
        """Test NULL_STREAM_ELEMENT constant."""
        assert NULL_STREAM_ELEMENT.element == ""
        assert NULL_STREAM_ELEMENT.element_type == "printable"
    
    def test_stream_element_pop_constant(self):
        """Test STREAM_ELEMENT_POP constant."""
        assert STREAM_ELEMENT_POP.element_type == "style_stack"
        assert STREAM_ELEMENT_POP.element.action == "pop"


class TestRuleResults:
    """Test RuleResults enum."""
    
    def test_rule_results_values(self):
        """Test RuleResults enum values."""
        assert RuleResults.MATCH.value == "match"
        assert RuleResults.NO_MATCH.value == "no_match"
        assert RuleResults.POSSIBLE.value == "possible"


class TestProcessOutput:
    """Test ProcessOutput dataclass."""
    
    def test_process_output_creation(self):
        """Test ProcessOutput creation."""
        stream = [NULL_STREAM_ELEMENT]
        remaining = "remaining text"
        
        output = ProcessOutput(stream=stream, remaining=remaining)
        assert output.stream == stream
        assert output.remaining == remaining


class TestConsumeResults:
    """Test ConsumeResults dataclass."""
    
    def test_consume_results_creation(self):
        """Test ConsumeResults creation."""
        inner = [NULL_STREAM_ELEMENT]
        remaining = "remaining text"
        
        results = ConsumeResults(inner=inner, remaining=remaining)
        assert results.inner == inner
        assert results.remaining == remaining