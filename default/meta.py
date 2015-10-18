"""LEXOR: META NodeParser

Obtains the meta information on a document. The meta information
can only be the started in the first line of the document. This can
be done by starting with a line which contains a key and a value

    key: value

or a horizontal rule

    ---

See the `HrNP` documentation for more info on how to make a horizontal
rule. To end the meta information we may finish with an empty line
or alternatively, a horizontal rule.

"""
import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Element, RawText

META_RE = re.compile(
    r'^(?P<b1>[ ]{0,3})(?P<key>[A-Za-z0-9_-]+)'
    r'(?P<b2>:\s*)(?P<value>.*)'
)
META_MORE_RE = re.compile(r'^(?P<blank>[ ]{4,})(?P<value>.*)')


class MetaNP(NodeParser):
    """Obtain the meta information. """

    def get_entry(self, parser, warn=True):
        """Examine a line of the text and get an entry. """
        index = parser.text.find('\n', parser.caret)
        if index == -1:
            return None
        line = parser.text[parser.caret:index].strip()
        if not line:
            return None
        match = META_RE.match(line)
        if match:
            pos = parser.copy_pos()
            b1 = match.group('b1')
            key = match.group('key').lower().strip()
            b2 = match.group('b2')
            value = match.group('value').strip()
            node = Element('entry', {'name': key}).set_position(*pos)
            val_node = RawText('item', value)
            blank = len(b1) + len(key) + len(b2)
            pos = parser.compute(parser.caret + blank)
            val_node.set_position(*pos)
            node.append_child(val_node)
            parser.update(index+1)
            search = True
            while search:
                index = parser.text.find('\n', parser.caret)
                if index == -1:
                    return node
                line = parser.text[parser.caret:index]
                match_more = META_MORE_RE.match(line)
                if match_more:
                    value = match_more.group('value')
                    val_node = RawText('item', value.strip())
                    blank = len(match_more.group('blank'))
                    pos = parser.compute(parser.caret + blank)
                    val_node.set_position(*pos)
                    node.append_child(val_node)
                    parser.update(index+1)
                else:
                    search = False
                    count = 0
                    try:
                        while line[count] == ' ':
                            count += 1
                    except IndexError:
                        pass
                    if count > 0:
                        self.msg('E101', parser.pos, [count])
            return node
        else:
            delimiter = parser['HrNP'].make_node()
            if delimiter is None and warn:
                self.msg('E100', parser.pos)
        return None

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if caret != 0:
            return None
        pos = parser.copy_pos()
        delimiter = parser['HrNP'].make_node()
        entry = self.get_entry(parser, False)
        if entry is None:
            return delimiter
        node = Element('lexor-meta').set_position(*pos)
        while entry is not None:
            node.append_child(entry)
            entry = self.get_entry(parser)
        return [node]

    def close(self, _):
        pass


MSG = {
    'E100': 'meta block not properly finished',
    'E101': 'indentation of {0} spaces not enough for meta value',
}
MSG_EXPLANATION = [
    """
    - Meta blocks end when with the encounter of the first blank line.

    - Alternatively, they men end with the encounter of the first
      horizontal rule.

    Okay:
        title:   My Document
        summary: A brief description of my document.
        authors: Manuel Lopez
                 Fulano de Tal
        date:    September 10, 2015
        blank-value:
        base_url: http://example.com

        This is the first paragraph of the document.

    E100:
        title:   My Document
        summary: A brief description of my document.
        authors: Manuel Lopez
                 Fulano de Tal
        date:    September 10, 2015
        blank-value:
        base_url: http://example.com
        This is the first paragraph of the document.

    E100:
        keyword: value
        This is the first paragraph.

""",
    """
    - A line is assumed to be an additional line of the value for the
      previous keyword if it is indented by 4 or more spaces.

    Okay:
        authors: Manuel Lopez
                 Fulano de Tal
        date:    September 10, 2015

    E101:
        authors: Manuel Lopez
          Fulano de Tal
        date:    September 10, 2015

"""
]
