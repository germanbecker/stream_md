import pytest
from stream_md.type_defs import RuleResults
from stream_md.tokens.block.leaf.table import Table,MAX_FIRST_COL
from tests.setup_test_environment import auto_setup_container




@pytest.mark.parametrize("s,end_stream,expected", [
    pytest.param("", False, (RuleResults.POSSIBLE, 0), id="1: empty string"),
    pytest.param(" a | b\n - | -\n", False, (RuleResults.MATCH, 0), id="2: Simple table"),
    pytest.param("hola soy un texto", False, (RuleResults.POSSIBLE, 0), id="3: One line: < MAX_FIRST_COL -> possible"),
    pytest.param("hola soy un texto" * 20, False, (RuleResults.NO_MATCH, None), id="4: One line: > MAX_FIRST_COL -> no_match"),
    ])
def test_rule(s,end_stream,expected):
    result = Table.rule(s,end_stream)
    assert result.result == expected[0]
    if expected[1] is not None:
        assert result.result != RuleResults.NO_MATCH
        assert result.position == expected[1]
    
