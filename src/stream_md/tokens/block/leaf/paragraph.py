from stream_md.tokens.base import DEFAULT_CONTAINER
from stream_md.type_defs import RuleResults,PreProcessOutput,ConsumeResults, StackStyleAction, StackStylePop, StackStylePush, StreamElement,StreamElementPrintable, StreamElementSyleStack, Style
from stream_md.tokens.block.base import BlockRuleResult,BlockMatch
from stream_md.tokens.block.leaf.base import LeafBlock
from stream_md.tokens.base import ProcessOutput

class Paragraph(LeafBlock):
    add_a_pop = True
    always_matches = True

    def __init__(self, cid=DEFAULT_CONTAINER):
        self.started: bool = False
        self.pop_style: bool = False
        super().__init__(cid)
    
    def _not_me(self,s:str):
        for block in self.all_blocks:
            if not isinstance(self,block):
                result = block.rule(s,cid=self.cid)
                if result.result == RuleResults.MATCH:
                    self.stack.pop(result.token)
                    return True
        return False

    @classmethod
    def rule(cls,s: str, end_stream: bool = False,cid = DEFAULT_CONTAINER) ->BlockRuleResult:
        #match always for now..
        return BlockMatch(cls(cid),0)


    def preprocess(self, input: str, end_stream: bool = False) -> PreProcessOutput:
        full_input = self.outer + input
        lines = full_input.splitlines(keepends=True)
        buf = ""
        if len(lines) == 0:
            return PreProcessOutput(processed=input, remaining="", done=False)
        else:
            i = 0
            while i < len(lines):
                if lines[i] != "\n" and not self._not_me(lines[i]):
                    buf += lines[i]
                    i += 1
                else:
                    self.done = True
                    break
            
        remaining="".join(lines[i:])
        if self.done and  not remaining:
            self.pop_style = True
        return PreProcessOutput(processed="".join(lines[:i])[len(self.outer):], remaining=remaining, done=self.done)

    def consume(self,input_text: str, end_stream: bool = False) -> ConsumeResults:
        #preprocess already selcted what is ours, so we consume everything
        inner: list[StreamElement] = []
        if not self.started:
            inner.append(StreamElementSyleStack(StackStylePush(Style(color="misty_rose3"))))
            self.started = True
        inner.append(StreamElementPrintable(input_text))
        return ConsumeResults( remaining="", inner=inner)


    def __str__(self):
        return f"Paragraph() <{id(self)}"
