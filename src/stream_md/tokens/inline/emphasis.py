from abc import ABC,abstractmethod
import string
from class_property import class_property

from rich.style import Style

from stream_md.tokens.base import RuleResult, Match, NoMatch, Possible
from stream_md.tokens.inline.base import ( MarkDownInline,
                                          )
                                          
from stream_md.type_defs import ( StreamElementPrintable,
                                 StreamElementSyleStack,
                                 StreamElement,
                                 ConsumeResults,
                                 PreProcessOutput,
                                 StackStylePush,
                                 NULL_STREM_ELEMENT,
                                 STREAM_ELEMT_POP,
                                 )

# ----------------------------------------
# Abstract base for emphasis-like tokens
# ----------------------------------------

class EmphasisToken(MarkDownInline, ABC):
    """Abstract base for * or ** emphasis tokens"""

    def __init__(self):
        super().__init__()
        self.done = False
        self.stack_element = StreamElementSyleStack(StackStylePush(self.get_style()))
        self.open_len = len(self.marker)
        self.outer = ""

    @classmethod
    def _classify(cls,s:str,i: int,end_stream: bool):
        mlen = len(cls.marker)
        n = len(s)
        prev_char = s[i-1] if i > 0 else None
        next_char = s[i+mlen] if i+mlen < n else None

        prev_is_space = prev_char is None or prev_char.isspace()
        next_is_space = next_char is None or next_char.isspace()
        

        prev_is_punct = prev_char in string.punctuation if prev_char else False
        next_is_punct = next_char in string.punctuation if next_char else False

        next_is_me = next_char == cls.marker[0] if next_char else False
        prev_is_me = prev_char == cls.marker[0] if prev_char else False


        if s[i:i+mlen] == cls.marker and (next_char or end_stream): #no confirmar nada si estamos en el ultimo
            can_open = ( not next_is_me and not prev_is_me and
                        not next_is_space and
                        ( not next_is_punct or ( next_is_punct and ( prev_is_space or prev_is_punct) )
                         )
                        )

            #can_open = (not next_is_space and not next_is_me and not prev_is_me) and (prev_is_space or prev_is_punct or prev_char is None)
            can_close = ( not next_is_me and not prev_is_me and 
                          not prev_is_space and 
                         ( not prev_is_punct or ( prev_is_punct and ( next_is_punct or next_is_space))
                          ))
            #can_close = (not prev_is_space and not next_is_me and not prev_is_me) and (next_is_space or next_is_punct or next_char is None)
        else:
            can_open, can_close = False,False
        return can_open, can_close

    @abstractmethod
    def get_style(self) -> Style:
        """Devuelve el estilo asociado a este token (italic, bold, etc.)"""
        raise NotImplementedError()

    def preprocess(self, input:str, end_stream: bool = False) -> PreProcessOutput:
        """
        If we find the closing marker,split the input and leave everyhing after closing marker as remaining
        """
        search_start = self.open_len +1
        full_outer  = self.outer + input
        close_idx = full_outer[search_start:].find(self.marker)
        for i in range(search_start,len(full_outer)- self.open_len +1):
            _,can_close = self._classify(full_outer,i,end_stream)
            if can_close:
                split_position = i - len(self.outer) + self.open_len 
                remaining = input[split_position:]
                if remaining or end_stream:  #only split if we know for sure this is the end
                    self.done = True
                    return PreProcessOutput(input[:split_position], remaining,True)


        return PreProcessOutput(input,"",False)
        

    def consume(self, input: str, end_stream: bool = False) -> ConsumeResults:
        if not input:
            return ConsumeResults(inner=[NULL_STREM_ELEMENT], remaining=input)

        delta: list[StreamElement] = []

        # push de estilo si no lo hemos hecho
        if not self.inner:
            delta.append(self.stack_element)
            input = input[self.open_len:]

        #ver si termina con el marker, el split ya lo hizo el preprocess
        if input.endswith(self.marker):
            delta.append(StreamElementPrintable(input[:-self.open_len])) #text up to the marker
            if self.done: # the end, accourding to preprocess
                delta.append(STREAM_ELEMT_POP)
                return ConsumeResults(inner=delta, remaining="")
            else: #may not be the end
                return ConsumeResults(inner=delta, remaining=self.marker)

        else:
            # todavía no encontramos cierre, consumimos todo como contenido
            delta.append(StreamElementPrintable(input))
            return ConsumeResults(inner=delta, remaining="")


    @classmethod
    def rule(cls, s: str,end_stream: bool = False) -> RuleResult:
        mlen = len(cls.marker)
        n = len(s)


        i = 0
        while i <= n - mlen:
            if s[i:i+mlen] == cls.marker:
                can_open, _ = cls._classify(s,i,end_stream)
                if can_open:
                    j = i + mlen
                    while j <= n - mlen:
                        if s[j:j+mlen] == cls.marker:
                            _, can_close = cls._classify(s,j,end_stream)
                            if can_close:
                                token = cls()  # instancia → push en stack
                                return Match(token=token, position=i)
                        j += 1
                    #have opining marker but no closing one
                    if not end_stream:
                        return Possible(position=i)
                    else:
                        #if we are at the end the opening marker is nothing
                        return NoMatch()
            i += 1
        #Return possible if the n-last charcaters match the first characters of self.marker
        if not end_stream:
            for i in range(len(cls.marker),0,-1):
                prefix = cls.marker[:i]
                if s.endswith(prefix):
                    return Possible(position= len(s) - len(prefix))
        return NoMatch()



# ----------------------------------------
# Concrete emphasis tokens
# ----------------------------------------

class Italic(EmphasisToken):

    @class_property
    def marker(self) -> str:
        return "*"

    def get_style(self):
        return Style(italic=True)

class Strong(EmphasisToken):
    @class_property
    def marker(self) -> str:
        return "**"
    def get_style(self):
        return Style(bold=True)
