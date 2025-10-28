"""
Test for the emphasis preprocess fix where closing markers at the very end 
of input should be properly found and consumed.

These tests FAIL with the buggy code and PASS with the fixed code.
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from stream_md.tokens.inline.emphasis import Italic, Strong
from stream_md.tokens.base import MarkdownContainer
from tests.setup_test_environment import auto_setup_container


class TestEmphasisEndMarkerFix:
    """Test that closing markers at end of input are properly handled"""
    
    def test_strong_end_marker_should_be_found(self):
        """
        FIXED: Strong emphasis ending exactly at input end should be found
        
        This test FAILS with buggy code, PASSES with fixed code.
        """
        strong = Strong()
        strong.outer = "**"  # Opening marker already consumed
        
        # Input is just the content + closing marker
        input_text = "hello**"
        
        # After fix: This should find the closing ** and set done=True
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Strong end marker test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}, remaining={result.remaining!r}")
        print(f"  Strong.done: {strong.done}")
        
        # These assertions FAIL with buggy code, PASS with fixed code
        assert result.done is True, "Should find closing marker and set done=True"
        assert strong.done is True, "Token should be marked as done"
        assert result.processed == "hello", "Should process text up to closing marker"
        assert result.remaining == "**", "Should leave closing marker as remaining for consume()"
    
    def test_italic_end_marker_should_be_found(self):
        """
        FIXED: Italic emphasis ending exactly at input end should be found
        """
        italic = Italic()
        italic.outer = "*"
        
        input_text = "hello*"
        result = italic.preprocess(input_text, end_stream=True)
        
        print(f"Italic end marker test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}, remaining={result.remaining!r}")
        
        # These assertions FAIL with buggy code, PASS with fixed code
        assert result.done is True, "Should find closing marker and set done=True"
        assert italic.done is True, "Token should be marked as done"
        assert result.processed == "hello", "Should process text up to closing marker"
        assert result.remaining == "*", "Should leave closing marker as remaining"
    
    def test_full_process_no_remaining_text(self):
        """
        FIXED: Full process should consume all text with no remaining
        
        This test ensures the fix prevents the "remaining content" warning.
        """
        strong = Strong()
        
        # Process complete strong text with end_stream=True
        input_text = "**hello**"
        result = strong.process(input_text, end_stream=True)
        
        print(f"Full process test:")
        print(f"  Input: {input_text!r}")
        print(f"  Remaining: {result.remaining!r}")
        print(f"  Strong.done: {strong.done}")
        
        # This assertion FAILS with buggy code (remaining="**"), PASSES with fixed code
        assert result.remaining == "", f"Should have no remaining text, but got: {result.remaining!r}"
        assert strong.done is True, "Strong token should be marked as done"
    
    def test_italic_full_process_no_remaining_text(self):
        """
        FIXED: Italic full process should also consume all text
        """
        italic = Italic()
        
        input_text = "*hello*"
        result = italic.process(input_text, end_stream=True)
        
        print(f"Italic full process test:")
        print(f"  Input: {input_text!r}")
        print(f"  Remaining: {result.remaining!r}")
        print(f"  Italic.done: {italic.done}")
        
        # This assertion FAILS with buggy code, PASSES with fixed code
        assert result.remaining == "", f"Should have no remaining text, but got: {result.remaining!r}"
        assert italic.done is True, "Italic token should be marked as done"
    
    def test_nested_emphasis_end_marker(self):
        """
        Test that the fix works for nested emphasis scenarios
        """
        # Test case: ***bold italic*** (strong + italic)
        strong = Strong()
        strong.outer = "**"
        
        # The strong token would process "*bold italic***"
        input_text = "*bold italic***"
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Nested emphasis test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}")
        
        # Should find the ** at the end
        assert result.done is True, "Should find closing ** even with nested content"
        assert result.processed == "*bold italic*", "Should process up to closing **"
        assert result.remaining == "**", "Should leave ** as remaining"
    
    def test_multiple_markers_at_end(self):
        """
        Test edge case with multiple markers at the end
        """
        strong = Strong()
        strong.outer = "**"
        
        # Input ends with multiple asterisks
        input_text = "hello****"  # Content + ** + **
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Multiple markers test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}")
        
        # Should find the first valid closing **
        assert result.done is True, "Should find first valid closing **"
        assert result.processed == "hello", "Should process up to first closing **"
        assert result.remaining == "****", "Should leave all markers as remaining"
    
    def test_marker_not_at_very_end_still_works(self):
        """
        Ensure the fix doesn't break cases where marker is not at the very end
        """
        strong = Strong()
        strong.outer = "**"
        
        input_text = "hello** world"  # Marker not at end
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Marker not at end test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}")
        
        # This should work correctly (and did work before the fix)
        assert result.done is True, "Should find closing ** even when not at end"
        assert result.processed == "hello", "Should process up to closing **"
        assert result.remaining == "** world", "Should leave marker and rest as remaining"


if __name__ == "__main__":
    MarkdownContainer.initialize()
    pytest.main([__file__, "-v", "-s"])