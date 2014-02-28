"""LEXOR: EMPTY NodeParser"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Text

RE = re.compile(r'\s*\n')


class EmptyNP(NodeParser):
    """Collect empty spaces. """

    @staticmethod
    def skip_space(parser, space=' \t'):
        """Moves the parser to the first nonspace character and
        returns the index where this happends."""
        index = parser.caret
        while parser.text[index:index+1] in space:
            index += 1
        parser.update(index)
        return index

    def make_node(self):
        parser = self.parser
        match = RE.match(parser.text, parser.caret)
        if match:
            data = parser.text[parser.caret:match.end()]
            parser.update(match.end())
            return Text(data)
        return None
