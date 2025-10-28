"""
Base class for block tokens
"""

from __future__ import annotations

from typing import Literal,Optional, Union, Type
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from rich.style import StyleStack,Style
import logging

from stream_md.type_defs import RuleResults, StreamElement, PreProcessOutput, ProcessOutput, ConsumeResults
from stream_md.tokens.base import TokenStack, Token, Match, Possible, NoMatch, FindChild, FoundChild, PossibleChild, NoChild

@dataclass(frozen=True)
class BlockMatch(Match):
    token: MarkDownBlock

BlockRuleResult = Union[BlockMatch,Possible, NoMatch]

class MarkDownBlock(Token):
    stack_style = False
    all_blocks: list[Type[MarkDownBlock]] = []
    always_matches = False #paragraph will set this to True

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not inspect.isabstract(cls):
            MarkDownBlock.all_blocks.append(cls)
    
    @classmethod
    @abstractmethod
    def rule(cls, s:str, end_stream: bool = False) -> BlockRuleResult:
        ...
    
    def find_block(self, input:str, end_stream: bool = False) -> FindChild:
        always_matches = [ block for block in self.all_blocks if block.always_matches]
        if len(always_matches) > 1:
            raise RuntimeError(f" there could only be one block that always matches")
        rest = [ block for block in self.all_blocks if not block.always_matches]
        possibles: list[Possible] = []
        for block in rest:
            result = block.rule(input,end_stream)
            if result.result == RuleResults.MATCH:
                return FoundChild(is_match=RuleResults.MATCH,token=result.token, position=result.position)
            elif result.result == RuleResults.POSSIBLE:
                possibles.append(result)
        if possibles:
            possibles.sort(key=lambda x : x.position)
            return PossibleChild(is_match=possibles[0].result, position= possibles[0].position)


        #now check if paragraph matches
        if always_matches:
            result = always_matches[0].rule(input,end_stream)
            if result.result == RuleResults.MATCH:
                return FoundChild(is_match=RuleResults.MATCH,token=result.token, position=result.position)
        return NoChild()
