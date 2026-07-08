from dataclasses import dataclass

from rich.style import Style
from stream_md.tokens.base import RuleResult, Match, NoMatch, Possible

from stream_md.tokens.inline.base import ( MarkDownInline,
                                          )
from stream_md.tokens.base import ( ProcessOutput,
                                   Token,
                                   FindChild,
                                   NoChild,
                                   Match,
                                   Possible,
                                   RuleResults,
                                   FoundChild,
                                   PossibleChild
                                   )

from stream_md.type_defs import ( StreamElementPrintable,
                                 StreamElementSyleStack,
                                 StreamElement,
                                 ConsumeResults,
                                 StackStylePush,
                                 StackStylePop,
                                 PreProcessOutput,
                                 StackStylePush,
                                 NULL_STREM_ELEMENT,
                                 STREAM_ELEMT_POP,
                                 
                                 )
from stream_md.tokens.inline.emphasis import EmphasisToken
BACK_TICK= '`'

@dataclass
class Marker:
    start: int
    len: int
    end: int | None = None

class CodeSpan(EmphasisToken):
    _style = Style(color="#F0F0F0", bgcolor="#404040")
    marker = ""
    def get_style(self):
        return self._style



    def __init__(self,marker_length: int):
        self.marker_length = marker_length
        self.marker = BACK_TICK * self.marker_length
        super().__init__()

    def preprocess(self, input_text: str, end_stream: bool = False) -> PreProcessOutput:
        full_outer = self.outer + input_text
        prev_len = len(self.outer)
        full_len = len(full_outer)
        i = self.marker_length #skip first marker
        while i < full_len:
            if ( full_outer[i:i+ self.marker_length] == BACK_TICK * self.marker_length and
                (i + self.marker_length or end_stream)):
                pivot = i - prev_len + self.marker_length
                self.done = True
                return PreProcessOutput(processed=input_text[:pivot],
                                        remaining=input_text[pivot:],
                                        done=True)
            i+= 1
        return PreProcessOutput(processed=input_text,
                                remaining="",
                                done=False)

            


    def find_child(self, input: str, end_stream: bool = False) -> FindChild:
        return NoChild()

    @classmethod
    def rule(cls, s: str, end_stream: bool = False) -> RuleResult:
        """
        If open and close are found in s (i.e. same marker length) return that
        If open is found but not close, return possible with the fist opening found
        else not return no match
        """

        def _offset_result(r: RuleResult, offset: int) -> RuleResult:
            if r.result == RuleResults.MATCH:
                return Match(r.token, r.position + offset)
            elif r.result == RuleResults.POSSIBLE:
                return Possible(position=r.position + offset)
            else:
                return r

        def _line_rule(s: str, end_stream: bool = False) ->RuleResult:
            """
            Helper funciton to run the rule on a sinlge line
            """
            markers: list[Marker] = []
            def find_marker(len: int) -> tuple[int,Marker] | None:
                for j,marker in enumerate(markers):
                    if marker.len == len:
                        return j,marker

            i = 0
            slen = len(s)
            found_new_line = False
            while i < slen:
                if s[i] == '\n': #we don't support multi-line code spans, otherwise we sould have to wait for the whole stream
                    found_new_line = True
                    break
                marker_length = 0
                while i+ marker_length < slen and s[i + marker_length] == BACK_TICK:
                    marker_length += 1
                if marker_length :
                    matching = find_marker(marker_length)
                    if matching and ( i + marker_length < slen or end_stream): #is it a valid end marker
                        if matching[0] == 0: #if it was the first marker -> match, else wait to see if the first one wraps this one
                            return Match(cls(marker_length),matching[1].start)
                        else: #store the end
                            matching[1].end = i #do we use it for something?
                    else:
                        markers.append(Marker(start=i,len=marker_length))

                i+= marker_length + 1

            if end_stream or found_new_line: #finish procesing: either full match or no match
                for marker in markers:
                    if marker.end:
                        return Match(cls(marker.len), marker.start)
                        
                else:
                    return NoMatch()
            elif markers:
                first_maerker = markers[0]
                if first_maerker.end:
                    return Match(cls(first_maerker.len), first_maerker.start)
                else:
                    return Possible(first_maerker.start)
            return NoMatch()

        line_result =NoMatch() #in case there are no lines
        offset = 0
        lines= s.splitlines(keepends=True)
        for line in lines[:-1]:
            line_result = _line_rule(line,end_stream=end_stream)
            if line_result.result == RuleResults.MATCH: #only the last line can produce "possible" since the others have a \n
                return _offset_result(line_result,offset)
            offset += len(line)

        if lines:
            last_line_result = _line_rule(lines[-1], end_stream=end_stream)
            return _offset_result(last_line_result,offset)
        return line_result
            


