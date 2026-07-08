import pytest
from stream_md.tokens.inline.code_span import CodeSpan
from stream_md.type_defs import RuleResults
from tests.setup_test_environment import auto_setup_container


pytest.param
@pytest.mark.parametrize("s,end_stream,expected", [
    pytest.param("hola", False, (RuleResults.NO_MATCH, None), id="1: No marks, no match"),
    pytest.param("`hola`", False, (RuleResults.POSSIBLE, 0), id="2: Simple possible match(end mark at the end)"),
    pytest.param("`hola`", True, (RuleResults.MATCH, 0), id="3: Mark at the end with end_stream: Match"),
    pytest.param("`hola`p", False, (RuleResults.MATCH, 0), id="4: End Mark not at the end: match"),
    pytest.param("```hola``` pija", False, (RuleResults.MATCH, 0),id="5: simple 3 ticks mark"),
    pytest.param("blabla```hola``` pija", False, (RuleResults.MATCH, 6),id="6: code span not at the start"),
    pytest.param("a: `hola ``inner``some more", False, (RuleResults.POSSIBLE, 3),id="7: inner completed without \\n or end_stream"),
    pytest.param("a: `hola ``inner``some \nmore", False, (RuleResults.MATCH, 9),id="8: inner completed with\\n "),
    pytest.param("a: `hola ``inner``some more", True, (RuleResults.MATCH, 9),id="9: inner completed with end stream\\n "),
    pytest.param("a: `hola ``inner with onether ```internal``` block `````and another one````` yeah``some more", 
                 True, (RuleResults.MATCH, 9),id="10: inner completed with end stream, with internal blocks ignored\\n "),
    pytest.param("random pija \n otra cosa `fence` lala",False, (RuleResults.MATCH, 24), id="11:Previous \\n -> should match"),
    pytest.param("random pija \n otra cosa `fence`\n",False, (RuleResults.MATCH, 24), id="12:Previous \\n, ends just in \\n -> should match"),
    pytest.param('us markdown elements\n- Some `',False, (RuleResults.POSSIBLE, 28), id="13:Ends ins marker"),

    ] )
def test_rule(s,end_stream,expected):
    result = CodeSpan.rule(s,end_stream)
    assert result.result == expected[0]
    if expected[1] is not None:
        assert result.position == expected[1]


