"""LEXOR: QUOTE NodeParser

Detetects quoted elements.

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import Element, Entity

EMPTY = ' \t\n\r\f\v'


class QuoteNP(NodeParser):
    """Looks for quotes. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        qchar = parser.text[caret:caret+1]
        if qchar not in "'\"":
            return None
        if parser.text[caret-1] not in EMPTY:
            parser.update(caret+1)
            return Entity(qchar)
        if parser.text[caret+1:caret+2] in EMPTY:
            parser.update(caret+1)
            return Entity(qchar)
        index = parser.text.find(qchar, caret+1)
        while index != -1:
            char = parser.text[index-1]
            if char == '\\':
                index = parser.text.find(qchar, index+1)
            elif char not in EMPTY:
                node = Element('quoted')
                node['char'] = qchar
                node.end_pos = index
                parser.update(parser.caret+1)
                return node
            else:
                break
        parser.update(parser.end)
        return Entity(qchar)

    def close(self, node):
        parser = self.parser
        if parser.caret != node.end_pos:
            return None
        del node.end_pos
        pos = parser.copy_pos()
        parser.update(parser.caret+1)
        return pos
