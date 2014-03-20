"""LEXOR: META NodeParser

Obtains the meta information on a document.

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import Element, RawText


class MetaNP(NodeParser):
    """Obtain the meta information. """

    @staticmethod
    def get_entry(parser):
        """Examine a line of the line and get an entry. """
        index = parser.text.find('\n', parser.caret)
        if index == -1:
            return None
        line = parser.text[parser.caret:index].split(':', 1)
        if len(line) != 2 or line[0][-1:] == '\\':
            return None
        node = RawText('entry', line[1].strip(), {'name': line[0]})
        parser.update(index+1)
        return node

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if caret != 0:
            return None
        entry = self.get_entry(parser)
        if entry is None:
            return None
        node = Element('lexor-meta')
        while entry is not None:
            node.append_child(entry)
            entry = self.get_entry(parser)
        return [node]
