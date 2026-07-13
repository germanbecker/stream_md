"""
Root block
"""

from typing import Tuple
import itertools

from stream_md.type_defs import StreamElementPrintable
from stream_md.tokens.base import DEFAULT_CONTAINER, PreProcessOutput, ProcessOutput,ConsumeResults, NoMatch
from stream_md.tokens.block.base import MarkDownBlock,BlockRuleResult



class Root(MarkDownBlock):

    find_child = MarkDownBlock.find_block


    def _split_empty_lines(self, s:str) -> Tuple[str,str]:
        lines = s.splitlines(keepends=True)
        # encontrar prefijo de líneas vacías
        prefix = list(itertools.takewhile(lambda l: l == "\n", lines))
        rest = lines[len(prefix):]
        return "".join(prefix), "".join(rest)



    def preprocess(self, input: str, end_stream: bool = False) -> PreProcessOutput:
        if self.is_last_token:
            before = self.outer 
            if not before or before[-1] == "\n": #if we start a new line, just print empty lines
                empty_lines, rest = self._split_empty_lines(input)
                self.delta.append(StreamElementPrintable( empty_lines))
                return PreProcessOutput(rest,"", False)
        return PreProcessOutput(input,"", False)

    def postprocess(self,input:ProcessOutput, end_stream: bool = False) -> ProcessOutput:
        delta = self.delta + input.stream
        self.delta = []
        return ProcessOutput(delta, input.remaining)

    def consume(self,input : str, end_stream: bool = False) -> ConsumeResults:
        return ConsumeResults([],input)


    @classmethod
    def rule(cls, s: str, end_stream: bool = False, cid: str= DEFAULT_CONTAINER) -> BlockRuleResult:
        return NoMatch()

