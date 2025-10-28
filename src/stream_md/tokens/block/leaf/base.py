from stream_md.tokens.block.base import MarkDownBlock
from stream_md.tokens.inline.base import MarkDownInline

class LeafBlock(MarkDownBlock):
    find_child = MarkDownInline.find_child
