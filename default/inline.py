"""LEXOR: INLINE NodeParsers

Here we define several parsers for inline patterns.

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import Element

EMPTY = ' \t\n\r\f\v'


class InlinePatternNP(NodeParser):
    """Abstract class for a few inline patterns. """

    def __init__(self, parser):
        """To be able to use the this class you need to derive a node
        parser from this abstract class. You only need to overload
        this method and define the following:

            self.parser = parser
            self.pattern = None
            self.tight = True  # No separation <pattern>text<pattern>
            self.tagname = None

        For instance: ("**", True, "strong") will transform

            `**strong**` into <strong>strong</strong>

        but not `**strong **`.
        """
        NodeParser.__init__(self, parser)
        self.pattern = None
        self.tight = True
        self.tagname = None

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        content_start = caret+len(self.pattern)
        if parser.text[caret:content_start] != self.pattern:
            return None
        content_end = parser.text.find(self.pattern, content_start)
        if content_end == -1 or content_start == content_end:
            return None
        if self.tight is True:
            char_start = parser.text[content_start]
            char_end = parser.text[content_end-1]
            if char_start in EMPTY or char_end in EMPTY:
                return None
        node = Element(self.tagname)
        node.pos = parser.copy_pos()
        node.inlinepattern_end = content_end
        parser.update(content_start)
        return node

    def close(self, node):
        parser = self.parser
        caret = parser.caret
        if caret != node.inlinepattern_end:
            return None
        pos = parser.copy_pos()
        parser.update(caret+len(self.pattern))
        parser['ElementNP'].get_attribute_list(parser, node)
        del node.inlinepattern_end
        return pos


class StrongNP(InlinePatternNP):
    """Parse text located between `**` and `**`. """

    def __init__(self, parser):
        InlinePatternNP.__init__(self, parser)
        self.pattern = "**"
        self.tagname = "strong"


class Strong2NP(InlinePatternNP):
    """Parse text located between `__` and `__`. """

    def __init__(self, parser):
        InlinePatternNP.__init__(self, parser)
        self.pattern = "__"
        self.tagname = "strong"


class EmNP(InlinePatternNP):
    """Parser text located between '*' and '*'. """

    def __init__(self, parser):
        InlinePatternNP.__init__(self, parser)
        self.parser = parser
        self.pattern = "*"
        self.tagname = "em"


class StrongEmNP(InlinePatternNP):
    """Checks for triple `*`. """

    def __init__(self, parser):
        InlinePatternNP.__init__(self, parser)
        self.parser = parser
        self.pattern = "***"
        self.tagname = "strong_em"


class EmStrongNP(InlinePatternNP):
    """Checks for triple `_`. """

    def __init__(self, parser):
        InlinePatternNP.__init__(self, parser)
        self.parser = parser
        self.pattern = "___"
        self.tagname = "em_strong"


class SmartEmNP(NodeParser):
    """Checks for _em_. """

    def make_node(self):
        parser = self.parser
        if parser.text[parser.caret] != '_':
            return None
        if parser.text[parser.caret-1] not in EMPTY:
            return None
        found = False
        index = parser.caret
        while found is False:
            index = parser.text.find('_', index+1, parser.end)
            if index == -1 or parser.text[index-1] in EMPTY:
                return None
            char = parser.text[index+1:index+2]
            if char.isalpha() or char in '&':
                pass
            else:
                found = True
        if parser.caret+1 == index:
            return None
        pos = parser.copy_pos()
        parser.update(parser.caret+1)
        node = Element('em')
        node.pos = pos
        node.smartem_end = index
        return node

    def close(self, node):
        parser = self.parser
        caret = parser.caret
        if caret != node.smartem_end:
            return None
        pos = parser.copy_pos()
        parser.update(caret+1)
        parser['ElementNP'].get_attribute_list(parser, node)
        del node.smartem_end
        return pos


