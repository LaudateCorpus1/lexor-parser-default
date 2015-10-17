"""LEXOR: PARAGRAPH NodeParser

Node parser description.

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Element
from lexor.util import Position

EMPTY_RE = re.compile(r'\s*\n')

# Only a few tags are allowed in p tags. Here is a reference:
# http://webdesign.about.com/od/htmltags/p/bltags_paragrap.htm
VALID_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'basefont', 'bdo', 'big', 'br',
    'button', 'cite', 'code', 'dfn', 'em', 'font', 'i', 'img',
    'input', 'kbd', 'label', 'map', 'object', 'q', 's', 'samp',
    'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup',
    'textarea', 'tt', 'u', 'var',
]
INVALID_TAGS = [
    'address', 'article', 'aside', 'blockquote', 'dir', 'div', 'dl',
    'fieldset', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'header', 'hgroup', 'hr', 'main', 'menu', 'nav', 'ol', 'p',
    'pre', 'section', 'table', 'ul',
]


class ParagraphNP(NodeParser):
    """Checks for valid paragraphs. """

    def make_node(self):
        """Returns a paragraph element. """
        parser = self.parser
        index = parser.caret
        try:
            while parser.text[index] in ' \t\n\r\f\v':
                index += 1
        except IndexError:
            parser.update(index)
            return None
        end = parser.end
        tmp = parser['AutoLinkNP'].is_auto_link(parser, index, end)
        if tmp is None:
            tmp = parser['AutoMailNP'].is_auto_mail(parser, index, end)
            if tmp is None:
                tmp = parser['ElementNP'].get_tagname(parser)
                if tmp is not None and tmp not in VALID_TAGS:
                    return None
        node = Element('p')
        node.pos = parser.copy_pos()
        return node

    def close(self, node):
        """Returns the position where the element was closed. """
        parser = self.parser
        caret = parser.caret
        tmp = parser['ElementNP'].get_tagname(parser)
        if tmp is not None and tmp in INVALID_TAGS:
            self.msg('E100', parser.pos, (Position(node.pos), tmp))
            return parser.copy_pos()
        if parser.text[caret] != '\n':
            return None
        match = EMPTY_RE.match(parser.text, parser.caret, parser.end)
        if match:
            if match.end(0)-caret > 1 or match.end(0) == parser.end:
                parser.update(match.end(0)-1)
                return parser.copy_pos()
        if node.parent.name == 'list_item':
            if (parser.text[caret+1:caret+3] == '%%' or
                    parser.text[caret+1:caret+8] == '</list>' or (
                    node.index == 0 and
                    parser.text[caret+1:caret+2] in '^+*')):
                node['lx-remove-wrap'] = 'true'
                return parser.copy_pos()
        return None

MSG = {
    'E100': 'paragraph at {0} closed due to opening tag `{1}`',
}
MSG_EXPLANATION = [
    """
    - Only a few tags are allowed as children of a `p` tag. The
      paragraph tag is forced to close when one of the following tags
      is encountered.

        'address', 'article', 'aside', 'blockquote', 'dir', 'div',
        'dl', 'fieldset', 'footer', 'form', 'h1', 'h2', 'h3', 'h4',
        'h5', 'h6', 'header', 'hgroup', 'hr', 'main', 'menu', 'nav',
        'ol', 'p', 'pre', 'section', 'table', 'ul',

    Okay:
        This is line 1 with <strong>bold</strong> font.
        This is line 2 with <em>italic</em> font.

    E100:
        This is line 1 with <h1>header 1</h1>.
        This is line 2 with <h2>header 2</h2>.
""",
]
