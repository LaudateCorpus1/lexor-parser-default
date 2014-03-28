"""LEXOR: HR NodeParser

Processes horizontal rules.

"""

import re
from lexor.core import NodeParser, Void
RE = re.compile(
    r'\n((-+[ ]{0,2}){3,}|(_+[ ]{0,2}){3,}|(\*+[ ]{0,2}){3,})[ ]*(\n|$)'
)


class HrNP(NodeParser):
    """Capture horizontal rules. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        match = RE.match(parser.text, caret-1)
        if match is None:
            return None
        parser.update(match.end())
        return Void('hr')
