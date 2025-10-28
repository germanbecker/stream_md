from stream_md.type_defs import RuleResults,PreProcessOutput,ConsumeResults,StreamElementPrintable
from stream_md.tokens.block.base import BlockRuleResult,BlockMatch
from stream_md.tokens.block.leaf.base import LeafBlock

class Paragraph(LeafBlock):
    always_matches = True
    
    def _not_me(self,s:str):
        for block in self.all_blocks:
            if not isinstance(self,block):
                result = block.rule(s)
                if result.result == RuleResults.MATCH:
                    self.stack.pop(result.token)
                    return True
        return False

    @classmethod
    def rule(cls,s: str, end_stream: bool = False) ->BlockRuleResult:
        #match always for now..
        return BlockMatch(cls(),0)


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
        return PreProcessOutput(processed="".join(lines[:i])[len(self.outer):], remaining="".join(lines[i:]), done=self.done)

    def consume(self,input: str, end_stream: bool = False) -> ConsumeResults:
        #preprocess already selcted what is ours, so we consume everything
        return ConsumeResults( remaining="", inner=[StreamElementPrintable(input)])
    def __str__(self):
        return f"Paragraph() <{id(self)}"
