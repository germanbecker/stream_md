"""
Test for the emphasis preprocess bug where closing markers at the end 
of input are not properly consumed, causing remaining text warnings.
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from stream_md.tokens.inline.emphasis import Italic, Strong
from stream_md.tokens.base import MarkdownContainer
from stream_md.type_defs import PreProcessOutput
from tests.setup_test_environment import auto_setup_container


class TestEmphasisPreprocessBug:
    """Test the preprocess bug where closing markers at end aren't consumed"""
    
    def test_strong_preprocess_bug_reproduction(self):
        """
        BUG: Strong emphasis ending at end of input not properly preprocessed
        
        For "**hello**" with end_stream=True, the preprocess should:
        1. Find the closing ** at position 7
        2. Set self.done = True
        3. Return processed text without the closing marker
        4. Leave no remaining text
        """
        # Create a Strong token and simulate it being opened
        strong = Strong()
        
        # Simulate the token has been opened (this would happen during rule matching)
        strong.outer = "**"  # The opening marker has been consumed
        
        # Test preprocessing the rest: "hello**"
        input_text = "hello**"
        
        # This should find the closing ** and mark as done
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Input: {input_text!r}")
        print(f"Preprocess result: processed={result.processed!r}, remaining={result.remaining!r}, done={result.done}")
        print(f"Strong.done: {strong.done}")
        
        # The bug: currently this fails because the closing ** isn't found
        assert result.done is True, "Should mark as done when closing marker found"
        assert strong.done is True, "Token should be marked as done"
        assert result.processed == "hello", "Should process text up to closing marker"
        assert result.remaining == "**", "Should leave closing marker as remaining for consume()"
    
    def test_italic_preprocess_bug_reproduction(self):
        """
        Test the same bug with italic markers
        """
        italic = Italic()
        italic.outer = "*"  # Opening marker consumed
        
        input_text = "hello*"
        result = italic.preprocess(input_text, end_stream=True)
        
        print(f"Italic - Input: {input_text!r}")
        print(f"Italic - Result: processed={result.processed!r}, remaining={result.remaining!r}, done={result.done}")
        
        assert result.done is True, "Italic should mark as done when closing marker found"
        assert result.processed == "hello", "Should process text up to closing marker"
        assert result.remaining == "*", "Should leave closing marker as remaining"
    
    def test_debug_preprocess_range_issue(self):
        """
        Debug the specific range issue in preprocess method
        """
        strong = Strong()
        strong.outer = "**"
        
        input_text = "hello**"
        full_outer = strong.outer + input_text  # "**hello**"
        search_start = strong.open_len + 1  # 3
        
        print(f"Debug info:")
        print(f"  full_outer: {full_outer!r} (length: {len(full_outer)})")
        print(f"  search_start: {search_start}")
        print(f"  open_len: {strong.open_len}")
        print(f"  range end: {len(full_outer) - strong.open_len} (should be {len(full_outer)})")
        
        # Current buggy range
        buggy_range = range(search_start, len(full_outer) - strong.open_len)
        print(f"  buggy range: {list(buggy_range)}")
        
        # Fixed range should be
        fixed_range = range(search_start, len(full_outer) - strong.open_len + 1)
        print(f"  fixed range: {list(fixed_range)}")
        
        # Test classification at each position
        for i in range(len(full_outer)):
            if i >= search_start:
                _, can_close = Strong._classify(full_outer, i, True)
                marker_at_pos = full_outer[i:i+strong.open_len] if i+strong.open_len <= len(full_outer) else "N/A"
                in_buggy = i in buggy_range
                in_fixed = i in fixed_range
                print(f"  pos {i}: '{marker_at_pos}' can_close={can_close}, in_buggy={in_buggy}, in_fixed={in_fixed}")
    
    def test_full_process_with_end_stream(self):
        """
        Test the full process method to see the remaining text issue
        """
        strong = Strong()
        
        # Process the complete strong text with end_stream=True
        input_text = "**hello**"
        
        # This simulates what happens when the token is created and processes the full input
        result = strong.process(input_text, end_stream=True)
        
        print(f"Full process result:")
        print(f"  input: {input_text!r}")
        print(f"  stream length: {len(result.stream)}")
        print(f"  remaining: {result.remaining!r}")
        print(f"  strong.done: {strong.done}")
        print(f"  strong.outer: {strong.outer!r}")
        print(f"  strong.inner length: {len(strong.inner)}")
        
        # The bug manifests as remaining text when there should be none
        assert result.remaining == "", f"Should have no remaining text, but got: {result.remaining!r}"
    
    def test_proposed_fix_logic(self):
        """
        Test the proposed fix for the range issue
        """
        def fixed_preprocess(self, input_text: str, end_stream: bool = False):
            """Fixed version of preprocess method"""
            search_start = self.open_len + 1
            full_outer = self.outer + input_text
            
            # FIXED: Include the last possible position for the marker
            for i in range(search_start, len(full_outer) - self.open_len + 1):
                _, can_close = self._classify(full_outer, i, end_stream)
                if can_close:
                    split_position = i - len(self.outer) + self.open_len
                    remaining = input_text[split_position:]
                    if remaining or end_stream:
                        self.done = True
                        return PreProcessOutput(input_text[:split_position], remaining, True)
            
            return PreProcessOutput(input_text, "", False)
        
        # Test the fixed version
        strong = Strong()
        strong.outer = "**"
        
        # Monkey patch the fixed method
        import types
        strong.preprocess = types.MethodType(fixed_preprocess, strong)
        
        input_text = "hello**"
        result = strong.preprocess(input_text, end_stream=True)
        
        print(f"Fixed preprocess result:")
        print(f"  processed: {result.processed!r}")
        print(f"  remaining: {result.remaining!r}")
        print(f"  done: {result.done}")
        
        assert result.done is True, "Fixed version should mark as done"
        assert result.processed == "hello", "Should process text correctly"
        assert result.remaining == "**", "Should leave marker as remaining"


if __name__ == "__main__":
    from stream_md.tokens.base import MarkdownContainer
    MarkdownContainer.initialize()
    pytest.main([__file__, "-v", "-s"])