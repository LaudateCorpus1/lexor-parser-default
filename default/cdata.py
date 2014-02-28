"""LEXOR: CDATA NodeParser

`CData` nodes are enclosed within `<![CDATA[` and `]]>`. These type
of nodes are useful because no parsing takes place inside the
content. The only restriction involved with these nodes is that the
character sequence `]]>` must not appear in the content.

In case there is a need to write `]]>` inside the character data then
you have to split the content into two `CData` nodes:

The correct way to write the following

    <![CDATA[Cannot have `]]>` inside.]]>

is

    <![CDATA[Cannot have `]]]]><![CDATA[>` inside.]]>

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import CData


class CDataNP(NodeParser):
    """Retrives the data enclosed within `<![CDATA[` and `]]>` and
    returns a `CData` node. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+9] != '<![CDATA[':
            return None
        index = parser.text.find(']]>', caret+9)
        if index == -1:
            self.msg('E100', parser.pos)
            parser.update(parser.end)
            return CData(parser.text[caret+9:parser.end])
        parser.update(index+3)
        return CData(parser.text[caret+9:index])


MSG = {
    'E100': '`]]>` not found',
}
MSG_EXPLANATION = [
    """
    - The terminating character sequence for the `CData` node was not
      found.

    Okay: <![CDATA[We can write a < b and M&Ms.]]>

    E100: <![CDATA[We can write a < b and M&Ms.
""",
]
