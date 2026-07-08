"""
base inline token
"""
from abc import abstractmethod
from typing import Tuple
import inspect
from class_property import class_property

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


class MarkDownInline(Token):
    """Base class for inline tokens"""
    all_inlines: list[type["MarkDownInline"]] = []

    def __init_subclass__(cls):
        super().__init_subclass__()
        if not inspect.isabstract(cls):
            MarkDownInline.all_inlines.append(cls)

    @class_property
    @abstractmethod
    def marker(self) -> str:
        ...

    def find_child(self, input: str, end_stream: bool = False) -> FindChild:
        if not input:
            return NoChild()
        possibles: list[Tuple[Match | Possible,int]] = []
        
        not_me = [ c for c in MarkDownInline.all_inlines if type(self) is not c]

        for inline_cls in not_me:
            result = inline_cls.rule(input, end_stream)
            if result.result != RuleResults.NO_MATCH:
                possibles.append((result,
                                  len(inline_cls.marker) if hasattr(inline_cls,"marker") and isinstance(inline_cls.marker, str) else 0))

        if possibles:
            # Primer match en texto
            possibles.sort(key=lambda x: (
                # Second criterion: matches over possibles (False sorts before True for is_possible)
                x[0].position,
                # Frist criterion: position (earlier positions first)
                x[0].result == RuleResults.POSSIBLE,  
                # Third criterion: marker length (longer markers take precedence)
                -x[1]
))
            winner = possibles[0][0]

            # Limpiar stack de los perdedores
            for loser in possibles[1:]:
                if loser[0].result == RuleResults.MATCH:
                    self.stack.pop(loser[0].token)
            if winner.result == RuleResults.MATCH:
                return FoundChild(
                    is_match=RuleResults.MATCH,
                    token=winner.token,
                    position=winner.position
                )
            else:
                return PossibleChild(
                    is_match=winner.result,
                    position=winner.position
                )

        return NoChild()

    def process(self, input: str, end_stream: bool = False) -> ProcessOutput:

        preresults = self.preprocess(input, end_stream)
        end_stream = end_stream and not preresults.remaining
        next = self.stack.next(self)

        if next:
            #process downstream token
            downstream = next.process(preresults.processed, end_stream or preresults.done)

        else:
            #first try to find a child if we are past the marker
            child_search_start = max(len(self.marker) + 1 - len(self.outer), #don't search the character right after the marker
                                     0) #if marker processed in previous calls, use the whole input
            child_serach_string = preresults.processed[child_search_start:]


            child_result = self.find_child(child_serach_string, end_stream or preresults.done) #if we are done it is the end of the stream for pottential childs
            if child_result.is_match != RuleResults.NO_MATCH:
                real_position = child_result.position + child_search_start
                #if there is a (potential) new child, only consume until the position. Leave the rest for follwoing invocation
                before = preresults.processed[:real_position]
                after = preresults.processed[real_position:]
            else:
                before = preresults.processed
                after = ""
            result = self.consume(before, end_stream and not after)

            #now we need to consume for the child otherwise we didnt consume any chars and the caller willl
            #wait for input forever
            if child_result.is_match == RuleResults.MATCH:
                next_result = child_result.token.process(after, end_stream or preresults.done)
                downstream = ProcessOutput(stream= result.inner + next_result.stream , remaining=result.remaining + next_result.remaining)
            else:
                downstream = ProcessOutput(stream = result.inner, remaining= result.remaining + after)
            if preresults.done and not downstream.remaining:
                if next:= self.stack.next(self):
                    #this shuoldn't happen
                    flushed = next.flush()
                    downstream = ProcessOutput(stream= flushed + downstream.stream, remaining= downstream.remaining)
                #remove ourselves from the stack
                self.stack.pop(self)


        postprocess_result = self.postprocess(downstream, end_stream)
        self.inner += postprocess_result.stream
        postprocess_result.remaining += preresults.remaining
        consumed_length = len(input) - len(postprocess_result.remaining)
        self.outer += input[:consumed_length]
        return postprocess_result
