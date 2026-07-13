import re

from rich.style import StyleStack, Style
from stream_md.type_defs import ( ConsumeResults,
                                 PreProcessOutput,
                                 StackStylePush, StreamElement,
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
from stream_md.tokens.block.leaf.paragraph import Paragraph
from stream_md.tokens.block.container.root import Root
from stream_md.tokens.base import MarkdownContainer
from stream_md.tokens.inline.code_span import CodeSpan
from rich.table import Table as RTable
from rich.text import Text


MAX_FIRST_COL = 180

class Table(LeafBlock):
    
    @staticmethod
    def _line_ends_table(s: str) -> bool :
        """
        Logic for lines that ends the table
        """
        if not s.endswith("\n"):
            return False
        if s == '\n':
            return True
        if s.strip().startswith(">") or s.strip().startswith("#"):
            return True
        return False
            
        
    def build_text(self, stream: list[StreamElement]) -> Text:
        style_stack = StyleStack(Style(color="#F0F0F0"))

        text = Text()
        for element in stream:
            if element.element_type == "style_stack":
                if element.element.action == "pop":
                    style_stack.pop()
                else:
                    style_stack.push(element.element.style)  
            else:
                if not ( isinstance(element.element,Text) or
                        isinstance(element.element, str)):
                    raise RuntimeError(f"{element.element} is of wrong isinstance for a table")
                text.append(element.element,
                    style=sum(style_stack._stack, Style())
                            )
        return text

    def subparse(self, s:str) -> list[StreamElement]:
        cid = "tp_" + s[:100]
        MarkdownContainer.initialize(cid=cid)
        subparser = Root(cid=cid)
        remaining = s
        stream = []
        result = subparser.process(s)
        remaining = result.remaining
        stream+= result.stream
        result = subparser.process(remaining,True)
        stream+= result.stream
        remaining = result.remaining
        while remaining:
            result = subparser.process(remaining,True)
            remaining = result.remaining
            stream+= result.stream

        return stream
                            
    def consume(self, input_text: str, end_stream: bool = False) -> ConsumeResults:
        #preprocess already separated what is ours
        if self.done:
            import ipdb
            #ipdb.set_trace()

            #tableplace_holder
            lines = (self.outer + input_text).splitlines()
            headers = self.split_row(lines[0])

            table = RTable(header_style=Style(bgcolor="#004040"))
            for column in headers:
                stream = self.subparse(column)
                table.add_column(self.build_text(stream))

            for row in lines[2:]:
                prow = []
                columns = self.split_row(row)
                for column in columns:
                    stream = self.subparse(column)
                    text = self.build_text(stream)
                    prow.append(text)

                table.add_row(*prow)

            return ConsumeResults(inner=[StreamElementPrintable(table)],remaining="")
        else:
            return ConsumeResults(inner=[], remaining=input_text)




    def preprocess(self, input_text: str, end_stream: bool = False) -> PreProcessOutput:
        full_outer = self.outer + input_text
        offset = len(self.outer)
        i = 0
        for line in full_outer.splitlines(keepends=True):
            if self._line_ends_table(line):
                self.done= True
                pivot = i
                break
            i+= len(line)
        else:
            pivot = i
        if end_stream:
            self.done = True
        r= PreProcessOutput(processed=input_text[:pivot-offset],
                                remaining=input_text[pivot-offset:],
                                done= self.done )
        return r




        return super().preprocess(input_text, end_stream)

    def find_block(self, input: str, end_stream: bool = False) -> FindChild:
        return NoChild()

    def find_child(self, input_text: str, end_stream: bool = False) -> FindChild:
        return NoChild()

    _delimiter_cell = re.compile(r'^:?-+:?$')

    @staticmethod
    def split_row(line: str) -> list[str]:
        # Sacamos el | inicial/final si los tiene (formato GFM típico: | a | b | c |)
        line = line.strip()
        if not line:
            return []
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]
        
        cells = re.split(r'(?<!\\)\|', line)
        return [c.strip().replace(r'\|', '|') for c in cells]

   
    @staticmethod
    def is_header(s: str) -> int:
        if "|" not in s:
            return 0
        cells = Table.split_row(s)
        if all(not Table._delimiter_cell.match(c.strip()) for c in cells):
            return len(cells)
        return 0 
            

    @staticmethod
    def no_delimiter(s: str) -> bool:
        "returns True if s cannot be a delimiter (conteains characters other than ' ' '| or '-')"
        return any(c not in " |-\n" for c in s)


    @staticmethod
    def is_delimiter(s: str) -> int:
        s = s.strip()
        if not s:
            return 0
        cells = Table.split_row(s)
        if not cells:
            return 0
        if len(cells) == 1 and '|' not in s:
            return 0
        if all(Table._delimiter_cell.match(c.strip()) for c in cells):
            return len(cells)
        else:
            return 0


    @classmethod
    def rule(cls, s:str, end_stream: bool = False, cid:str = DEFAULT_CONTAINER) -> BlockRuleResult:
        #Rules for blocks always receive full lines at the begining
        # we should only match the first line
        lines = s.splitlines(keepends=True)
        if len(lines) < 2:
            if not end_stream and (len (s) < MAX_FIRST_COL or "|" in s): # we are not supporting single column tables
                return Possible(0)
            else:
                return NoMatch()
        header = cls.is_header(lines[0])
        if not header:
            return NoMatch()
        if cls.no_delimiter(lines[1]):
            return NoMatch()
        if end_stream or lines[1].endswith("\n"):
            delimiter = cls.is_delimiter(lines[1])
            if header == delimiter:
                return BlockMatch(cls(cid=cid),0)
            else:
                return NoMatch()
        else:
            return Possible(0)
