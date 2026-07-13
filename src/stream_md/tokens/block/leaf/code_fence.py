import re
from typing import Optional, Tuple, Callable, TypeAlias
from rich.syntax import Syntax
from rich.text import Text
from rich.style import Style

from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.util import ClassNotFound

from stream_md.type_defs import ( ConsumeResults,
                                 PreProcessOutput,
                                 StackStylePush,
                                 StreamElementPrintable,
                                 StreamElementSyleStack,
                                 STREAM_ELEMT_POP,
                                 )
from stream_md.tokens.base import ( DEFAULT_CONTAINER, NoChild,
                                   FindChild,
                                   Possible,
                                   NoMatch,
                                   Match
                                   )

from stream_md.tokens.block.base import ( BlockRuleResult, BlockMatch)



from stream_md.tokens.block.leaf.base import LeafBlock

MultiLineSplitter: TypeAlias = Callable[[list[str]],int]

def python_muiltiline_string(lines: list[str]) -> int:
    """
    Split preprocess to contain start and end of multilne string
    """
    multilines = ['"""', "'''" ]
    multiline_start = None
    multiline_start_string:str|None = None
    for i,line in enumerate(lines):
        if multiline_start is None:
            for multiline in multilines:
                if line.count(multiline) == 1: #only if it appears exactly once
                    multiline_start = i
                    multiline_start_string = multiline
                    break
        else:
            if multiline_start_string and multiline_start_string in line:
                multiline_start = None
                multiline_start_string = None
    if multiline_start is None:
        multiline_start = len(lines) 
    return multiline_start




class StreamSyntax(Syntax):
    """
    modified Styntax class to remove newlines unless the block is done
    """
    def __init__(self,done:bool = False, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self._md_done =done
    def highlight(self, code: str, line_range: Optional[Tuple[Optional[int], Optional[int]]] = None) -> Text:
        text=  super().highlight(code, line_range)
        if not self._md_done:
            text.remove_suffix("\n")
        return text

class CodeFence(LeafBlock):
    fence_re = re.compile(r'^[ ]{0,3}(`{3,}|~{3,})(.*$)')
    posible_re = re.compile(r'^[ ]{0,3}(`+|~+)$')

    _multiline_splitters: dict[str,MultiLineSplitter] = { "python" : python_muiltiline_string } 

    def find_child(self, input: str, end_stream: bool) -> FindChild:
        return NoChild()

    def __init__(self, fence: str, language: str, cid:str = DEFAULT_CONTAINER):
        super().__init__(cid=cid)
        self.language = language
        self.fence = fence
        self.end_re = re.compile(rf"^[ ]{{0,3}}{self.fence}{self.fence[0]}*\s*$")
        self.possible_end_res = [ re.compile(rf"^[ ]{{0,3}}{self.fence[0]}*$"), #0 a 3 espacios seguidos de 0 o mas ` Y NADA MAS
                                 re.compile(rf"^[ ]{{0,3}}{self.fence}{self.fence[0]}*\s*$") ] #0 a 3 espacios mas el fence mas extra` mas espacios
        self.stack_element = StreamElementSyleStack(StackStylePush(Style(color="blue")))

    @classmethod
    def rule(cls, s:str, end_stream: bool = False, cid:str = DEFAULT_CONTAINER) -> BlockRuleResult:
        lines = s.splitlines()
        if not lines:
            if not end_stream:
                return Possible(0)
            else:
                return NoMatch()
        s = lines[0]
        m = cls.fence_re.match(s)
        if m:
            instance = cls(m.group(1), m.group(2), cid=cid)
            return BlockMatch(instance,0)
        elif cls.posible_re.match(s) and s[-1] != "\n" and not end_stream:
            return Possible(0)

        return NoMatch()

    def preprocess(self, input: str, end_stream: bool = False) -> PreProcessOutput:
        full_input = self.outer + input
        lines = full_input.splitlines(keepends=True)
        if not lines:
            self.done = end_stream
            return PreProcessOutput(processed=input, remaining="",done=end_stream)

        if not self.inner and lines[0][-1] == "\n": # update language
            m = self.fence_re.match(lines[0])
            if m:
                self.fence = m.group(1)
                self.language = m.group(2).strip()

        i = len(full_input) # in case we don't enter the loop
        for i,line in enumerate(lines[1:],1):
            if self.end_re.match(line):
                if line[-1] == '\n': #if we have the coplete line
                    self.done = True
                break

        if end_stream:
            self.done = True #regardless of whether we found the end
        else: #unless end_stream, check multiline
            if  self.language in self._multiline_splitters:
                i = self._multiline_splitters[self.language](lines[1:i+1])
        
        out = "".join(lines[:i+1])[len(self.outer):]
        remaining = "".join(lines[i+1:])
        return PreProcessOutput(processed=out, remaining= remaining,done=self.done)

    def consume(self, input: str, end_stream: bool = False) -> ConsumeResults:
        out = ""
        lines = input.splitlines(keepends=True)
        if not self.inner: #first input
            if lines[0][-1] != "\n": #first line not done, keep waiting
                return ConsumeResults(inner=[], remaining=input)
            else:
                self.delta.append(self.stack_element)
            lines = lines[1:] #skip first line
        if not lines:
            return ConsumeResults(inner=self.delta,remaining="")
        remaining = ""
        i = len(lines) # to make pyright happy
        for i,line in enumerate(lines):
            if self.end_re.match(line):
                if line[-1] != "\n" and not end_stream:
                    remaining = line
                else:
                    self.done = True
                break
            elif not end_stream and line[-1] != "\n" and any(r.match(line) for r in self.possible_end_res): #maybe it's the end
                remaining = line
                break #if line does not end in \n there should be no more lines, but just in case
            elif line[-1] == "\n" or end_stream : #only consume complete lines
                out +=line
            else: #incomplete line
                remaining = line
                break
        if out:
            if not self.language:
                lexer = guess_lexer(out)
            else:
                try:
                    lexer = get_lexer_by_name(self.language)
                except ClassNotFound:
                    lexer = guess_lexer(out)

            syntax = StreamSyntax(done=self.done,code=out, lexer=lexer)
            self.delta.append( StreamElementPrintable(syntax))
        if self.done:
            self.delta.append(STREAM_ELEMT_POP)

        remaining += "".join(lines[i+1:])
        return ConsumeResults(inner=self.delta,remaining=remaining)
