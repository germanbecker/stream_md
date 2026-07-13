import re
from rich.style import Style

from stream_md.type_defs import ( StackStylePush,
                                 STREAM_ELEMT_POP,
                                 PreProcessOutput,
                                 ConsumeResults,
                                 StreamElement,
                                 StreamElementSyleStack,
                                 StreamElementPrintable,
                                 NULL_STREM_ELEMENT,
                                 )

from stream_md.tokens.base import (
                                 DEFAULT_CONTAINER,
                                 Possible,
                                 NoMatch,
                                 )

from stream_md.tokens.block.base import ( BlockRuleResult, BlockMatch )

from stream_md.tokens.block.leaf.base import LeafBlock

heading_re = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)")
possible_heading_re = re.compile(r'^[ ]{0,3}#{1,6} ?$')
class Heading(LeafBlock):
    styles: dict[int,Style]= {
            1: Style(color="green"),
            2: Style(color="green"),
            3: Style(color="green"),
            4: Style(color="magenta"),
            5: Style(dim=True, color="cyan"),
            6: Style(dim=True, color="yellow"),
        }
    stack_style = True
    def __init__(self,level:int, cid:str = DEFAULT_CONTAINER):
        self.level = level
        super().__init__(cid=cid)

        self.ire = re.compile(fr"\s*{'#' * level}\s*(.*)")
        self.style_stack.push(self.styles[level])
        sp = StackStylePush(self.styles[level])
        se = StreamElementSyleStack(sp)
        self.stack_element = se
        self.done = False

    @classmethod
    def rule(cls,s: str, end_stream: bool = False, cid:str = DEFAULT_CONTAINER) -> BlockRuleResult:
        #do not assume this is the start of the line
        lines = s.splitlines(keepends=True)
        if not lines:
            return Possible(0)
        s = lines[0]
        if m := heading_re.match(s):
            token = cls(level= len(m.group(1)), cid=cid)
            return BlockMatch(token,position=0)
        if possible_heading_re.match(s) and not end_stream:
            return Possible(0)
        if s in {'', ' ', '  ', '   '} and not end_stream:
            return Possible(0)
        return NoMatch()


    def preprocess(self, input, end_stream: bool = False)-> PreProcessOutput:
        if not input:
            return PreProcessOutput(input,"", False)
        self.delta = [ ]
        temp = input.splitlines(keepends=True)
        self.thisline = temp[0]
        self.remaining = "".join(temp[1:])
        self.done = len(temp) > 1 or self.thisline.endswith("\n")
        return PreProcessOutput(self.thisline, self.remaining,self.done)


    def consume(self,input: str, end_stream: bool = False) -> ConsumeResults:
        if not input:
            return ConsumeResults(inner=[NULL_STREM_ELEMENT], remaining=input)
        this_line = input #preprocess already checked this
        delta: list[StreamElement] = []
        if not self.inner:
            delta.append(self.stack_element)
        delta.append(StreamElementPrintable(this_line))
        if this_line.endswith("\n"):
            delta.append(  STREAM_ELEMT_POP)
            self.done = True
        else:
            self.done = False

        return ConsumeResults(inner=delta,remaining="")

    def __str__(self):
        return f"Heading({self.level}) <{id(self)}>"
