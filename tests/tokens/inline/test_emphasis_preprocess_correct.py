"""
Test for the emphasis preprocess fix with correct understanding.

preprocess() splits input into:
- processed: text to consume in this call
- remaining: text to leave for next call  
- done: whether we found the closing marker

When end_stream=True: should consume everything and set done=True if closing found
When end_stream=False: should be conservative and leave potential markers
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from stream_md.tokens.inline.emphasis import Italic, Strong
from stream_md.tokens.base import MarkdownContainer
from tests.setup_test_environment import auto_setup_container


class TestEmphasisPreprocessCorrect:
    """Test preprocess with correct understanding of its purpose"""
    
    def test_strong_end_stream_true_should_consume_all(self):
        """
        When end_stream=True, should consume everything and set done=True
        
        This test FAILS with buggy code because done=False, PASSES with fixed code.
        """
        strong = Strong()
        strong.outer = "**"  # Opening marker already consumed
        
        input_text = "hello**"
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Strong end_stream=True test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: processed={result.processed!r}, remaining={result.remaining!r}, done={result.done}")
        print(f"  Strong.done: {strong.done}")
        
        # With end_stream=True, should consume everything and mark as done
        assert result.processed == "hello**", "Should consume all input when end_stream=True"
        assert result.remaining == "", "Should have no remaining when end_stream=True"
        assert result.done is True, "Should set done=True when closing marker found at end"
        assert strong.done is True, "Token should be marked as done"
    
    def test_strong_end_stream_false_should_be_conservative(self):
        """
        When end_stream=False, should be conservative about potential markers
        """
        strong = Strong()
        strong.outer = "**"
        
        input_text = "hello**"
        result = strong.preprocess(input_text, end_stream=False)
        
        print(f"Strong end_stream=False test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: processed={result.processed!r}, remaining={result.remaining!r}, done={result.done}")
        
        # With end_stream=False, should be conservative
        # (The exact behavior here depends on implementation, but done should be False)
        assert result.done is False, "Should not be done when end_stream=False"
    
    def test_italic_end_stream_true_should_consume_all(self):
        """
        Same test for italic markers
        """
        italic = Italic()
        italic.outer = "*"
        
        input_text = "hello*"
        result = italic.preprocess(input_text, end_stream=True)
        
        print(f"Italic end_stream=True test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: processed={result.processed!r}, remaining={result.remaining!r}, done={result.done}")
        
        assert result.processed == "hello*", "Should consume all input when end_stream=True"
        assert result.remaining == "", "Should have no remaining when end_stream=True"
        assert result.done is True, "Should set done=True when closing marker found"
        assert italic.done is True, "Token should be marked as done"
    
    def test_full_process_integration(self):
        """
        Test the full process() method to ensure no remaining text
        
        This is the real test - ensuring the markdown renderer doesn't get
        remaining text warnings.
        """
        strong = Strong()
        
        input_text = "**hello**"
        result = strong.process(input_text, end_stream=True)
        
        print(f"Full process integration test:")
        print(f"  Input: {input_text!r}")
        print(f"  Stream elements: {len(result.stream)}")
        print(f"  Remaining: {result.remaining!r}")
        print(f"  Strong.done: {strong.done}")
        print(f"  Strong.outer: {strong.outer!r}")
        
        # This is the key test - no remaining text should prevent warnings
        assert result.remaining == "", f"Should have no remaining text, got: {result.remaining!r}"
    
    def test_italic_full_process_integration(self):
        """
        Same integration test for italic
        """
        italic = Italic()
        
        input_text = "*hello*"
        result = italic.process(input_text, end_stream=True)
        
        print(f"Italic full process integration test:")
        print(f"  Input: {input_text!r}")
        print(f"  Remaining: {result.remaining!r}")
        print(f"  Italic.done: {italic.done}")
        
        assert result.remaining == "", f"Should have no remaining text, got: {result.remaining!r}"
    
    def test_debug_why_preprocess_fails(self):
        """
        Debug exactly why preprocess fails to find the closing marker
        """
        strong = Strong()
        strong.outer = "**"
        input_text = "hello**"
        
        # Manually replicate the preprocess logic to debug
        search_start = strong.open_len + 1  # 3
        full_outer = strong.outer + input_text  # "**hello**"
        
        print(f"Debug preprocess failure:")
        print(f"  full_outer: {full_outer!r} (length {len(full_outer)})")
        print(f"  search_start: {search_start}")
        print(f"  open_len: {strong.open_len}")
        
        # Current range (buggy)
        current_end = len(full_outer) - strong.open_len  # 9 - 2 = 7
        print(f"  current range: {list(range(search_start, current_end))}")
        
        # Check each position
        for i in range(len(full_outer)):
            if i >= search_start:
                marker = full_outer[i:i+strong.open_len] if i+strong.open_len <= len(full_outer) else "N/A"
                _, can_close = Strong._classify(full_outer, i, True)
                in_range = i < current_end
                print(f"    pos {i}: '{marker}' can_close={can_close} in_current_range={in_range}")
        
        # The bug: position 7 has the closing marker but isn't in the range!
        assert full_outer[7:9] == "**", "Closing marker should be at position 7"
        _, can_close_7 = Strong._classify(full_outer, 7, True)
        assert can_close_7 is True, "Position 7 should be able to close"
        assert 7 not in range(search_start, current_end), "BUG: Position 7 not in current range"
    
    def test_marker_in_middle_still_works(self):
        """
        Ensure fix doesn't break cases where marker is in the middle
        """
        strong = Strong()
        strong.outer = "**"
        
        input_text = "hello** world"
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Marker in middle test:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: processed={result.processed!r}, remaining={result.remaining!r}, done={result.done}")
        
        # Should find the marker and split correctly
        assert result.done is True, "Should find closing marker in middle"
        # The exact split depends on implementation details


if __name__ == "__main__":
    MarkdownContainer.initialize()
    pytest.main([__file__, "-v", "-s"])