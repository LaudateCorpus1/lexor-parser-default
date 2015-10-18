"""LEXOR: HR NodeParser

Processes horizontal rules. There are specified by three or more
of `-`, `*` or `_`. You may also add space in between them. For
instance:

    - - -

    * * *

    _ _ _

Make sure to leave one blank line above it otherwise you will be
defining a a header.

"""
import re
from lexor.core import NodeParser, Void
RE = re.compile(
    r'((-+[ ]{0,2}){3,}|(_+[ ]{0,2}){3,}|(\*+[ ]{0,2}){3,})[ ]*(\n|$)'
)


class HrNP(NodeParser):
    """Capture horizontal rules. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if caret > 1 and parser.text[caret-1] != '\n':
            return None

        match = RE.match(parser.text, caret)
        if match is None:
            return None

        node = Void('hr').set_position(*parser.pos)
        parser.update(match.end())
        return node

    def close(self, _):
        pass
