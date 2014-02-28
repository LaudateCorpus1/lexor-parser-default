"""LEXOR: ENTITY NodeParser

Some characters are special in HTML and LaTeX. This parser identifies
them and places them in an Entity node.

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Entity, Text, Void

RE = re.compile('.*?[ \t\n\r\f\v;]')


class EntityNP(NodeParser):
    """Processes special characters. This parser should be called
    only after all the other processors have attempted to parse."""
    escape = '<`*_[]()+-.!'
    tex = '\\{}$&#^_%~'

    @staticmethod
    def _handle_amp(parser, caret):
        """Helper function for EntityNP. """
        match = RE.search(parser.text, caret)
        if not match:
            parser.update(caret+1)
            return Entity('&')
        if parser.text[match.end()-1] != ';':
            parser.update(caret+1)
            return Entity('&')
        parser.update(match.end())
        return Entity(parser.text[caret:match.end()])

    def _handle_lt(self, parser, caret):
        """Helper function for make_node. """
        if parser.text[caret+1:caret+2] == '/':
            tmp = parser.text.find('>', caret+2)
            if tmp == -1:
                parser.update(caret+1)
                return Entity('<')
            else:
                stray_endtag = parser.text[caret:tmp+1]
                self.msg('E100', parser.pos, [stray_endtag])
                parser.update(tmp+1)
                return Text('')
        else:
            parser.update(caret+1)
            return Entity('<')

    def _handle_escape(self, parser, caret):
        """Helper function for make_node. """
        try:
            char = parser.text[caret+1]
        except IndexError:
            parser.update(caret+1)
            return Text('\\')
        if char in self.tex:
            node = Entity('\\%s' % char)
            parser.update(caret+2)
        elif parser.text[caret:caret+10] == '\\backslash':
            node = Entity('\\backslash')
            parser.update(caret+10)
        elif char in self.escape:
            node = Entity('\\%s' % char)
            parser.update(caret+2)
        else:
            node = Text('\\')
            parser.update(caret+1)
        return node

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret] == '&':
            return self._handle_amp(parser, caret)
        if parser.text[caret] == '<':
            return self._handle_lt(parser, caret)
        if parser.text[caret] != '\\':
            return None
        return self._handle_escape(parser, caret)


class BreakNP(NodeParser):
    """Obtains the line break. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+2] == '\\\\':
            parser.update(parser.caret+2)
            return Void('br')
        return None


MSG = {
    'E100': 'ignoring stray end tag `{0}`',
}
MSG_EXPLANATION = [
    """
    - Stray end tags are common when writing html tags. If you wish
      to display the stray tag then you should escape the components
      of the stray tag or wrap with backticks.

    Okay:
        This is a stray tag: \\</p>

    Okay:
        This is an example of a stray tag `</p>`

    E100: This is a stray tag: </p>
""",
]
