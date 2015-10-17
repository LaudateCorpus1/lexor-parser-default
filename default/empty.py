"""LEXOR: EMPTY NodeParser"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Text

RE = re.compile(r'\s*\n')


class EmptyNP(NodeParser):
    """Collect empty spaces. """

    @staticmethod
    def skip_space(parser, space=' \t'):
        """Moves the parser to the first non-space character and
        returns the index where this happened."""
        index = parser.caret
        char = parser.text[index:index+1]
        while char and char in space:
            index += 1
            char = parser.text[index:index+1]
        parser.update(index)
        return index

    def make_node(self):
        parser = self.parser
        match = RE.match(parser.text, parser.caret)
        if match:
            pos = parser.copy_pos()
            data = parser.text[parser.caret:match.end()]
            parser.update(match.end())
            return Text(data).set_position(*pos)
        return None
