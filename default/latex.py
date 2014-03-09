"""LEXOR: LATEX NodeParser

Processes LaTeX elements.

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import RawText, Entity

EMPTY = ' \t\n\r\f\v'
MAP = {
    '$': '$',
    '\\(': '\\)',
    '$$': '$$',
    '\\[': '\\]'
}


class LatexDisplayNP(NodeParser):
    """Parse text enclosed by $$, \\[. """

    def make_node(self):
        parser = self.parser
        if parser.text[parser.caret] not in ['$', '\\']:
            return None
        caret = parser.caret
        start = parser.text[caret:caret+2]
        if start in ['$$', '\\[']:
            index = parser.text.find(MAP[start], caret+2, parser.end)
            if index == -1:
                self.msg('E100', parser.pos)
                parser.update(caret+1)
                return Entity(start[0])
            node = RawText('latex', parser.text[caret+2:index])
            node['type'] = 'display'
            node['char'] = start[0]
            parser.update(index+2)
            return node
        return None


class LatexInlineNP(NodeParser):
    """Parse text enclosed by $, \\(. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+2] == '\\(':
            start = parser.text[caret:caret+2]
        elif parser.text[caret:caret+1] == '$':
            start = parser.text[caret:caret+1]
        else:
            return None
        if start == '$' and parser.text[caret+1:caret+2] in EMPTY:
            parser.update(caret+1)
            return Entity('$')
        index = parser.text.find(MAP[start], caret+1, parser.end)
        if start == '\\(' and index != -1:
            node = RawText('latex', parser.text[caret+2:index])
            node['type'] = 'inline'
            node['char'] = start[0]
            parser.update(index+2)
            return node
        while index != -1:
            char = parser.text[index-1]
            if char == '\\':
                index = parser.text.find('$', index+1, parser.end)
            elif char not in EMPTY:
                node = RawText('latex', parser.text[caret+1:index])
                node['type'] = 'inline'
                node['char'] = start[0]
                parser.update(index+1)
                return node
            else:
                break
        parser.update(caret+1)
        return Entity('$')


MSG = {
    'E100': 'unfinished display LaTeX enviroment',
}
MSG_EXPLANATION = [
    """
    - Display LaTeX enviroment start with `$$` or `\\[` and end with
      `$$` or `\\]`. If you wish to display them then consider
      escaping them, i.e. `\\$\\$`.

    Okay:
        $$\\sum$$

    E100:
        $$\\sum
""",
]
