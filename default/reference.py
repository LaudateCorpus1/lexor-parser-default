"""LEXOR: REFERENCE NodeParser

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Void, Element

RE = re.compile(r'\s+')
RE_INLINE = re.compile(r'.*?[ \t\n\r\f\v)]')
RE_NOSPACE = re.compile(r'.*?[ \t\n\r\f\v]')


class ReferenceBlockNP(NodeParser):
    """Parses reference blocks. These are the following ways to
    write these blocks:

        [ref]: url "title" Attributes

        [ref]: url Attributes

        [ref]: url Attributes
               "title"

        [ref]: url "title" { Attributes }

        {att_ref}: Attributes

        {att_ref}: { Attributes }

    Note that this node parser will get activated if it matches
    `[ref]:` or `{att_ref}:`. If your line will start with this
    then escape `[` or `{`.

    Returns a node with one of the following names:

        'address_reference'
        'attribute_reference'

    """

    def is_title(self, parser, line_end=None):
        """Return a string enclosed by quotes (single or double) and
        the index where it the parser should continue reading. Return
        none if there is no title. The optional argument should be
        the index until the parser is allowed to look for the title.
        By default it looks till the end of the line. """
        caret = parser.caret
        char = parser.text[caret:caret+1]
        if char not in "\"'":
            return None
        if line_end is None:
            line_end = parser.text.find('\n', caret)
            if line_end == -1 and parser.text[caret:].strip() != '':
                line_end = parser.end
                self.msg('E100', parser.compute(parser.end))
        index = parser.text.find(char, caret+1, line_end)
        if index == -1:
            return None
        title = re.sub(RE, ' ', parser.text[caret+1:index])
        return [title, index+1]

    def is_block_reference(self, parser):
        """Checks to see if the parser is placed at a block
        reference. If it is, then it returns the node that will hold
        the information. The returned node will have two properties:
        pos and line_end. Make sure to delete them before returning
        the node. """
        empty = 0
        index = parser.caret
        char = parser.text[index:index+1]
        while char in ' \t':
            if char == ' ':
                empty += 1
            else:
                empty += 4
            index += 1
            char = parser.text[index:index+1]
        if empty > 3 or char not in '[{':
            return None
        parser.update(index)
        ref_begin = index + 1
        if char == '[':
            closing_char = ']'
            tagname = 'address_reference'
        else:
            closing_char = '}'
            tagname = 'attribute_reference'
        line_end = parser.text.find('\n', ref_begin)
        if line_end == -1:
            line_end = parser.end
            self.msg('E100', parser.compute(parser.end))
        index = parser.text.rfind(closing_char, ref_begin, line_end)
        if index == -1:
            return None
        if parser.text[index+1] != ':':
            return None
        node = Void(tagname)
        node.line_end = line_end
        node['_reference_name'] = parser.text[ref_begin:index]
        node['_pos'] = parser.copy_pos()
        parser.update(index+2)
        parser['EmptyNP'].skip_space(parser)
        return node

    def update_link_ref(self, parser, node):
        """parse the rest of the line of the link reference. """
        match = RE_NOSPACE.search(
            parser.text, parser.caret, node.line_end+1
        )
        if match:
            end = match.end(0)
        else:
            if node.line_end != parser.end:
                self.msg('E101', node['_pos'])
                node['_address'] = ''
                return
            end = parser.end + 1
        node['_address'] = parser.text[parser.caret:end-1]
        if node['_address'] == '':
            self.msg('E101', node['_pos'])
        parser.update(end-1)
        parser['EmptyNP'].skip_space(parser)
        tmp = self.is_title(parser)
        if tmp:
            node['title'] = tmp[0]
            parser.update(tmp[1])
        index = parser.text.find('{', parser.caret, node.line_end)
        title_under = False
        if index == -1:
            title_under = True
            index = node.line_end
        if parser.text[parser.caret:index].strip() != '':
            parser['ElementNP'].read_attributes(parser, node, index)
        parser['EmptyNP'].skip_space(parser)
        parser['ElementNP'].get_attribute_list(parser, node)
        if title_under is True and 'title' not in node:
            parser.update(node.line_end+1)
            parser['EmptyNP'].skip_space(parser)
            tmp = self.is_title(parser)
            if tmp:
                index = parser.text.find('\n', tmp[1])
                text = parser.text[tmp[1]:index].strip()
                if text != '':
                    self.msg('E102', parser.pos)
                else:
                    node['title'] = tmp[0]
                    parser.update(tmp[1])

    def make_node(self):
        parser = self.parser
        node = self.is_block_reference(parser)
        if node is None:
            return None
        if node.name == 'attribute_reference':
            if parser.text[parser.caret] != '{':
                parser['ElementNP'].read_attributes(
                    parser, node, node.line_end
                )
            else:
                parser['ElementNP'].get_attribute_list(parser, node)
        else:
            self.update_link_ref(parser, node)
        del node.line_end
        return node


def check_parity(parser, index):
    """Returns the parity of '[]' and the index where it ends. """
    parity = 1
    while index < parser.end:
        char = parser.text[index]
        prev_l = parser.text[index-5:index]
        prev_r = parser.text[index-6:index]
        if char == '[' and prev_l != '\\left':
            parity += 1
        elif char == ']' and prev_r != '\\right':
            parity -= 1
        if parity == 0:
            break
        index += 1
    return parity, index


def get_inline_id(parser, node):
    """Assumes that the parser is positioned at '['"""
    if parser.text[parser.caret:parser.caret+1] == '[':
        ref_begin = parser.caret+1
    elif parser.text[parser.caret:parser.caret+2] == ' [':
        ref_begin = parser.caret+2
    else:
        return
    parity, ref_end = check_parity(parser, ref_begin)
    if parity != 0:
        return None
    parser.update(ref_begin)
    match = RE_NOSPACE.search(parser.text, parser.caret, ref_end)
    if match:
        node['_reference_id'] = parser.text[parser.caret:match.end(0)-1]
        parser.update(match.end(0))
        parser['EmptyNP'].skip_space(parser)
        if parser.text[parser.caret:ref_end].strip() != '':
            parser['ElementNP'].read_attributes(parser, node, ref_end, 0)
        parser.update(ref_end+1)
    else:
        node['_reference_id'] = parser.text[parser.caret:ref_end]
        parser.update(ref_end+1)


class ReferenceInlineNP(NodeParser):
    """Parses inline references.

        ![alt text](url) or ![alt text](url "title")
        [text](url) or [text](url "title")

        ![alt text][2] or ![alt text] [2]
        [Google][3] or [Google] [3]

        ![alt text]
        [Google]

    """
    active = False

    def get_inline_info(self, parser, node):
        """Assumes that the parser is positioned at ("""
        end_info = parser.text.find(")", parser.caret+1, parser.end)
        if end_info == -1:
            self.msg('E103', node['_pos'], parser.copy_pos())
            node.name = 'failed_%s' % node.name
            return
        parser.update(parser.caret+1)
        match = RE_INLINE.search(parser.text, parser.caret, end_info+1)
        if match:
            url = parser.text[parser.caret:match.end(0)-1]
            if node.name == 'img':
                node['src'] = url
            else:
                node['href'] = url
            parser.update(match.end(0))
            parser['EmptyNP'].skip_space(parser)
            tmp = parser['ReferenceBlockNP'].is_title(parser, end_info)
            if tmp:
                node['title'] = tmp[0]
                parser.update(tmp[1])
            if parser.text[parser.caret:end_info].strip() != '':
                parser['ElementNP'].read_attributes(
                    parser, node, end_info, 0
                )
            parser.update(end_info+1)
        del node['_pos']

    def make_node(self):
        parser = self.parser
        if parser.text[parser.caret] not in '![':
            return None
        if parser.text[parser.caret] == '!':
            tagtype = 'img'
            if parser.text[parser.caret+1:parser.caret+2] != '[':
                return None
            ref_begin = parser.caret+2
        else:
            tagtype = 'a'
            ref_begin = parser.caret+1

        parity, ref_end = check_parity(parser, ref_begin)
        if parity != 0:
            return None

        if tagtype == 'img':
            node = Void('reference')
            node['alt'] = parser.text[ref_begin:ref_end]
            node['_pos'] = parser.copy_pos()
            parser.update(ref_end+1)
            char = parser.text[ref_end+1:ref_end+2]
            if char == '(':
                node.name = 'img'
                self.get_inline_info(parser, node)
            elif char in '[ ':
                get_inline_id(parser, node)
            else:
                parser.update(ref_end+1)
            parser['ElementNP'].get_attribute_list(parser, node)
            return node
        node = Element('reference')
        node.pos = parser.copy_pos()
        node['_pos'] = parser.copy_pos()
        node.ref_end = ref_end
        parser.update(parser.caret+1)
        return node

    def close(self, node):
        parser = self.parser
        if parser.caret != node.ref_end:
            return None
        parser.update(parser.caret+1)
        char = parser.text[node.ref_end+1:node.ref_end+2]
        if char == '(':
            node.name = 'a'
            self.get_inline_info(parser, node)
        elif char in '[ ':
            get_inline_id(parser, node)
        else:
            parser.update(node.ref_end+1)
        parser['ElementNP'].get_attribute_list(parser, node)
        del node.ref_end
        return parser.copy_pos()

MSG = {
    'E100': 'no newline at end of file',
    'E101': 'invalid link reference',
    'E102': 'possible reference title detected',
    'E103': 'incomplete inline reference at {0}:{1:2}'
}
MSG_EXPLANATION = [
    """
    - The last line should have a newline.

    Reports E100.

""", """
    - When using link references you must provide the an address.
      This can be a url or a local address.

    - If you did not meant to provide a link reference then escape
      `[`.

    Okay:
        [math_url]: http://www.mathematics.uh.edu/

    E101:
        [math_url]:

""", """
    - Titles are allowed to be under the link reference. When this
      is the case you may not write text right after it.

    - If you did not meant to write a title then leave an empty line
    after the reference to get rid of message E102.

    Okay:
        [math_url]: http://www.mathematics.uh.edu/
                    "UH Math Website"

    E102:
        [math_url]: http://www.mathematics.uh.edu/
                    "UH Math Website". No content allowed in this line.

""", """
    - An inline reference was detected due to the opening of '(' but
      its closing character ')' was not found. As a result, the inline
      reference will not have a src or href attribute.

    Okay:
        This is a [link to google](http://google.com)

    E103:
        This is a [link to google](http://google.com

"""
]
