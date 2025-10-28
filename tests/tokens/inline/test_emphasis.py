"""
Tests for emphasis tokens (italic and bold)
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from stream_md.tokens.inline.emphasis import Italic, Strong, EmphasisToken
from stream_md.tokens.base import RuleResults, Match, Possible, NoMatch, MarkdownContainer
from tests.setup_test_environment import auto_setup_container


class TestEmphasisClassification:
    """Test the _classify method that determines if a marker can open/close"""
    
    def test_italic_can_open_basic(self):
        """Test basic cases where italic marker can open"""
        # *word - can open at start
        can_open, can_close = Italic._classify("*word", 0, False)
        assert can_open is True
        assert can_close is False
        
        # space*word - can open after space
        can_open, can_close = Italic._classify(" *word", 1, False)
        assert can_open is True
        assert can_close is False
    
    def test_italic_can_close_basic(self):
        """Test basic cases where italic marker can close"""
        # word* - can close at end
        can_open, can_close = Italic._classify("word*", 4, True)
        assert can_open is False
        assert can_close is True
        
        # word*space - can close before space
        can_open, can_close = Italic._classify("word* ", 4, False)
        assert can_open is False
        assert can_close is True
    
    def test_italic_cannot_open_after_space(self):
        """Test that italic cannot open when next char is space"""
        # * word - cannot open when followed by space
        can_open, can_close = Italic._classify("* word", 0, False)
        assert can_open is False
        assert can_close is False
    
    def test_italic_cannot_close_before_space(self):
        """Test that italic cannot close when prev char is space"""
        # word * - cannot close when preceded by space
        can_open, can_close = Italic._classify("word *", 5, False)
        assert can_open is False
        assert can_close is False
    
    def test_consecutive_markers(self):
        """Test behavior with consecutive markers like **"""
        # ** - first * cannot open/close when followed by *
        can_open, can_close = Italic._classify("**", 0, False)
        assert can_open is False
        assert can_close is False
        
        # ** - second * cannot open/close when preceded by *
        can_open, can_close = Italic._classify("**", 1, False)
        assert can_open is False
        assert can_close is False


class TestStrongClassification:
    """Test the _classify method for strong (bold) markers"""
    
    def test_strong_can_open_basic(self):
        """Test basic cases where strong marker can open"""
        # **word - can open at start
        can_open, can_close = Strong._classify("**word", 0, False)
        assert can_open is True
        assert can_close is False
    
    def test_strong_can_close_basic(self):
        """Test basic cases where strong marker can close"""
        # word** - can close at end
        can_open, can_close = Strong._classify("word**", 4, True)
        assert can_open is False
        assert can_close is True
    
    def test_strong_cannot_open_after_space(self):
        """Test that strong cannot open when followed by space"""
        # ** word - cannot open when followed by space
        can_open, can_close = Strong._classify("** word", 0, False)
        assert can_open is False
        assert can_close is False


class TestEmphasisRules:
    """Test the rule method that determines matches"""
    
    def test_italic_complete_match(self):
        """Test complete italic matches"""
        result = Italic.rule("*hello*", False)
        print(f"Result: {result}, Type: {type(result)}")
        # Let's see what we actually get first
        assert result is not None
    
    def test_italic_complete_match_end_stream(self):
        """Test complete italic matches at end of stream"""
        result = Italic.rule("*hello*", True)
        print(f"End stream result: {result}, Type: {type(result)}")
        # Let's see what we actually get first
        assert result is not None
    
    def test_italic_no_closing_possible(self):
        """Test italic with opening but no closing - should return Possible"""
        result = Italic.rule("*hello", False)
        print(f"No closing result: {result}, Type: {type(result)}")
        assert isinstance(result, Possible)
        assert result.position == 0
    
    def test_italic_no_closing_end_stream(self):
        """Test italic with opening but no closing at end of stream - should return NoMatch"""
        result = Italic.rule("*hello", True)
        print(f"No closing end stream result: {result}, Type: {type(result)}")
        assert isinstance(result, NoMatch)
    
    def test_strong_complete_match(self):
        """Test complete strong matches"""
        result = Strong.rule("**hello**", False)
        print(f"Strong result: {result}, Type: {type(result)}")
        assert result is not None
    
    def test_strong_no_closing_possible(self):
        """Test strong with opening but no closing - should return Possible"""
        result = Strong.rule("**hello", False)
        assert isinstance(result, Possible)
        assert result.position == 0
    
    def test_no_match_cases(self):
        """Test cases that should return NoMatch"""
        # No markers at all
        result = Italic.rule("hello world", False)
        assert isinstance(result, NoMatch)


class TestEmphasisEdgeCases:
    """Test edge cases and potential bugs"""
    
    def test_empty_string(self):
        """Test behavior with empty string"""
        result = Italic.rule("", False)
        assert isinstance(result, NoMatch)
        
        result = Italic.rule("", True)
        assert isinstance(result, NoMatch)
    
    def test_only_marker(self):
        """Test behavior with only the marker"""
        result = Italic.rule("*", False)
        print(f"Single marker result: {result}, Type: {type(result)}")
        # This should return Possible because we might get more input
        assert isinstance(result, Possible)
        assert result.position == 0
        
        result = Italic.rule("*", True)
        # At end of stream, single marker should be NoMatch
        assert isinstance(result, NoMatch)
    
    def test_punctuation_rules(self):
        """Test the punctuation rules in classification"""
        # Test cases with punctuation
        can_open, can_close = Italic._classify("(*word*)", 1, False)
        # After punctuation, should be able to open
        assert can_open is True
        
        can_open, can_close = Italic._classify("(*word*)", 6, False)
        # Before punctuation, should be able to close
        assert can_close is True


class TestEmphasisBugs:
    """Test specific bugs found in the code"""
    
    def test_marker_length_consistency(self):
        """Test that marker lengths are consistent"""
        assert len(Italic.marker) == 1
        assert len(Strong.marker) == 2
        
        # Test that the open_len is set correctly
        italic = Italic()
        assert italic.open_len == 1
        
        strong = Strong()
        assert strong.open_len == 2
    
    def test_classification_edge_cases(self):
        """Test edge cases in the _classify method"""
        # Test at string boundaries
        can_open, can_close = Italic._classify("*", 0, True)
        print(f"Single * at end: can_open={can_open}, can_close={can_close}")
        
        # Test with punctuation combinations
        can_open, can_close = Italic._classify(".*.", 1, False)
        print(f"Between dots: can_open={can_open}, can_close={can_close}")


class TestSpecificBugReproduction:
    """Test to reproduce and verify specific bugs"""
    
    def test_debug_italic_rule_logic(self):
        """Debug the italic rule logic step by step"""
        text = "*hello*"
        print(f"\\nDebugging rule logic for: '{text}'")
        
        # Test each position manually
        for i in range(len(text)):
            if text[i] == '*':
                can_open, can_close = Italic._classify(text, i, False)
                print(f"Position {i} ('{text[i]}'): can_open={can_open}, can_close={can_close}")
        
        # Test with end_stream=True
        print("\\nWith end_stream=True:")
        for i in range(len(text)):
            if text[i] == '*':
                can_open, can_close = Italic._classify(text, i, True)
                print(f"Position {i} ('{text[i]}'): can_open={can_open}, can_close={can_close}")
        
        # Now test the full rule
        result = Italic.rule(text, False)
        print(f"\\nRule result (end_stream=False): {result}")
        
        result = Italic.rule(text, True)
        print(f"Rule result (end_stream=True): {result}")


if __name__ == "__main__":
    # Setup container for direct execution
    MarkdownContainer.initialize()
    pytest.main([__file__, "-v", "-s"])