"""
Test for the emphasis preprocess bug where closing markers at the very end 
of input are not found due to incorrect range calculation.

BUG: In preprocess(), the range excludes the last valid position for closing markers.
FIX: Change range(search_start, len(full_outer) - self.open_len) 
     to range(search_start, len(full_outer) - self.open_len + 1)
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from stream_md.tokens.inline.emphasis import Italic, Strong
from stream_md.tokens.base import MarkdownContainer
from tests.setup_test_environment import auto_setup_container


class TestEmphasisEndMarkerBug:
    """Test the specific bug with end markers not being found"""
    
    def test_strong_end_marker_bug_demonstration(self):
        """
        Demonstrate the bug: Strong emphasis ending exactly at input end
        """
        strong = Strong()
        strong.outer = "**"  # Opening marker already consumed
        
        # Input is just the content + closing marker
        input_text = "hello**"
        
        # BUG: This should find the closing ** and set done=True
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"BUG DEMONSTRATION:")
        print(f"  Input: {input_text!r}")
        print(f"  Expected: done=True, processed='hello', remaining='**'")
        print(f"  Actual: done={result.done}, processed={result.processed!r}, remaining={result.remaining!r}")
        
        # This assertion will fail due to the bug
        # assert result.done is True, "Should find closing marker and set done=True"
        
        # Show that the bug causes the closing marker to be consumed as text
        assert result.done is False, "BUG: Currently fails to find closing marker"
        assert result.processed == "hello**", "BUG: Consumes closing marker as text"
        assert result.remaining == "", "BUG: No remaining text means marker was consumed"
    
    def test_italic_end_marker_bug_demonstration(self):
        """
        Same bug affects italic markers
        """
        italic = Italic()
        italic.outer = "*"
        
        input_text = "hello*"
        result = italic.preprocess(input_text, end_stream=True)
        
        print(f"ITALIC BUG:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}")
        
        assert result.done is False, "BUG: Italic also fails to find closing marker"
        assert result.processed == "hello*", "BUG: Consumes closing * as text"
    
    def test_range_calculation_analysis(self):
        """
        Analyze the exact range calculation issue
        """
        strong = Strong()
        strong.outer = "**"
        input_text = "hello**"
        
        # Replicate the preprocess logic
        search_start = strong.open_len + 1  # 3
        full_outer = strong.outer + input_text  # "**hello**"
        
        # Current buggy range calculation
        buggy_end = len(full_outer) - strong.open_len  # 9 - 2 = 7
        buggy_range = list(range(search_start, buggy_end))  # [3, 4, 5, 6]
        
        # Correct range calculation
        correct_end = len(full_outer) - strong.open_len + 1  # 9 - 2 + 1 = 8
        correct_range = list(range(search_start, correct_end))  # [3, 4, 5, 6, 7]
        
        print(f"RANGE ANALYSIS:")
        print(f"  full_outer: {full_outer!r} (length {len(full_outer)})")
        print(f"  search_start: {search_start}")
        print(f"  buggy_end: {buggy_end} -> range {buggy_range}")
        print(f"  correct_end: {correct_end} -> range {correct_range}")
        print(f"  closing marker at position: 7")
        print(f"  position 7 in buggy range: {7 in buggy_range}")
        print(f"  position 7 in correct range: {7 in correct_range}")
        
        # Verify the closing marker is at position 7 and can close
        closing_pos = 7
        marker_at_pos = full_outer[closing_pos:closing_pos+strong.open_len]
        _, can_close = Strong._classify(full_outer, closing_pos, True)
        
        print(f"  marker at pos {closing_pos}: {marker_at_pos!r}")
        print(f"  can_close at pos {closing_pos}: {can_close}")
        
        assert marker_at_pos == "**", "Closing marker should be at position 7"
        assert can_close is True, "Position 7 should be able to close"
        assert 7 not in buggy_range, "BUG: Position 7 not in current range"
        assert 7 in correct_range, "FIX: Position 7 should be in corrected range"
    
    def test_edge_cases_for_range_fix(self):
        """
        Test edge cases to ensure the range fix doesn't break other scenarios
        """
        # Test case 1: Marker not at the very end
        strong = Strong()
        strong.outer = "**"
        input_text = "hello** world"  # Closing marker not at end
        
        result = strong.preprocess(input_text, end_stream=True)
        print(f"EDGE CASE 1 - marker not at end:")
        print(f"  Input: {input_text!r}")
        print(f"  Result: done={result.done}, processed={result.processed!r}")
        
        # This should work correctly even with current code
        # (though we're not asserting since we haven't fixed it yet)
        
        # Test case 2: No closing marker at all
        strong2 = Strong()
        strong2.outer = "**"
        input_text2 = "hello world"
        
        result2 = strong2.preprocess(input_text2, end_stream=True)
        print(f"EDGE CASE 2 - no closing marker:")
        print(f"  Input: {input_text2!r}")
        print(f"  Result: done={result2.done}, processed={result2.processed!r}")
        
        assert result2.done is False, "Should not be done when no closing marker"
    
    def test_manual_fix_verification(self):
        """
        Manually implement the fix and verify it works
        """
        def fixed_preprocess(self, input_text: str, end_stream: bool = False):
            """Fixed version of preprocess with corrected range"""
            from stream_md.type_defs import PreProcessOutput
            
            search_start = self.open_len + 1
            full_outer = self.outer + input_text
            
            # FIXED: Include the last possible position
            for i in range(search_start, len(full_outer) - self.open_len + 1):
                _, can_close = self._classify(full_outer, i, end_stream)
                if can_close:
                    split_position = i - len(self.outer) + self.open_len
                    remaining = input_text[split_position:]
                    if remaining or end_stream:
                        self.done = True
                        return PreProcessOutput(input_text[:split_position], remaining, True)
            
            return PreProcessOutput(input_text, "", False)
        
        # Test the fix
        strong = Strong()
        strong.outer = "**"
        input_text = "hello**"
        
        # Apply the fixed method
        import types
        strong.preprocess = types.MethodType(fixed_preprocess, strong)
        
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"MANUAL FIX TEST:")
        print(f"  Input: {input_text!r}")
        print(f"  Fixed result: done={result.done}, processed={result.processed!r}, remaining={result.remaining!r}")
        
        assert result.done is True, "Fixed version should find closing marker"
        assert result.processed == "hello", "Should process text up to marker"
        assert result.remaining == "**", "Should leave closing marker as remaining"
        assert strong.done is True, "Token should be marked as done"
    
    def test_integration_with_full_process(self):
        """
        Test how this bug affects the full process() method
        """
        # This test shows the end-to-end impact of the bug
        strong = Strong()
        
        # Process complete strong text
        input_text = "**hello**"
        result = strong.process(input_text, end_stream=True)
        
        print(f"INTEGRATION TEST:")
        print(f"  Input: {input_text!r}")
        print(f"  Process result: remaining={result.remaining!r}")
        print(f"  Strong done: {strong.done}")
        
        # The bug should manifest as remaining text
        # (We're not asserting the fix since we haven't implemented it yet)
        print(f"  BUG IMPACT: Remaining text will cause warnings in markdown.py")


if __name__ == "__main__":
    MarkdownContainer.initialize()
    pytest.main([__file__, "-v", "-s"])