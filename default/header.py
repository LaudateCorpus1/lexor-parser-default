"""LEXOR: HEADER NodeParser

Lexor supports two types of headers: setext and atx.

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Element
SETEXT_RE = re.compile(r'^.*?\n[=-]+[ ]*(\n|$)', re.MULTILINE)


class AtxHeaderNP(NodeParser):
    """Parses header elements in the atx style. """

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret] != '#':
            return None
        index = parser.caret + 1
        level = 1
        while parser.text[index:index+1] == '#':
            index += 1
            level += 1
            if level == 6:
                break
        tagname = 'h%d' % level
        node = Element(tagname)
        node.pos = parser.copy_pos()
        # Get attributes if they follow right after the hash
        parser.update(index)
        parser['ElementNP'].get_attribute_list(parser, node)
        # Get index where content starts
        content_start = parser['EmptyNP'].skip_space(parser)
        # Get indices of the left and right bracket
        index = parser.text.find('\n', content_start, parser.end)
        if index == -1:
            index = parser.end
        final_pos = index + 1
        att = False
        left_b = None
        right_b = parser.text.rfind('}', content_start, index)
        if right_b != -1:
            if parser.text[right_b+1:index].strip() == '':
                left_b = parser.text.rfind('{', parser.caret, right_b)
                char = parser.text[left_b-1]
                if left_b != -1 and char in ' \t#':
                    att = True
        # Get the index where the content ends
        if att is True:
            content_end = left_b
        else:
            content_end = index
        index = content_end - 1
        # Check if there are extra hashes so that we can ignore them
        while parser.text[index] in ' \t\r\f\v':
            index -= 1
        while parser.text[index] == '#':
            index -= 1
        if parser.text[index+1:index+2] == '#':
            content_end = index+1
        node.content_end = content_end
        node.att = att
        node.left_b = left_b
        node.final_pos = final_pos
        return node

    def close(self, node):
        parser = self.parser
        caret = parser.caret
        if node.content_end != caret:
            return None
        pos = parser.copy_pos()
        if node.att is True:
            parser.update(node.left_b)
            parser['ElementNP'].get_attribute_list(parser, node)
        parser.update(node.final_pos)
        parser['ElementNP'].get_attribute_list(parser, node)
        del node.att
        del node.left_b
        del node.content_end
        del node.final_pos
        return pos


class SetextHeaderNP(NodeParser):
    """Parses header elements. """

    def make_node(self):
        """Returns a header element."""
        parser = self.parser
        match = SETEXT_RE.match(parser.text, parser.caret, parser.end)
        if match is None:
            return None
        index = parser.text.find('\n', parser.caret, parser.end)

        level = 1
        if parser.text[index+1] == '-':
            level = 2
        node = Element('h%d' % level)
        node.pos = parser.copy_pos()

        content_start = parser['EmptyNP'].skip_space(parser)
        final_pos = match.end(0)
        att = False
        left_b = None
        right_b = parser.text.rfind('}', content_start, index)
        if right_b != -1:
            if parser.text[right_b+1:index].strip() == '':
                left_b = parser.text.rfind('{', parser.caret, right_b)
                if left_b != -1 and parser.text[left_b-1] in ' \t':
                    att = True
        # Get the index where the content ends
        if att is True:
            content_end = left_b
        else:
            content_end = index

        node.content_end = content_end
        node.att = att
        node.left_b = left_b
        node.final_pos = final_pos
        return node

    def close(self, node):
        """Returns the position where the element was closed. """
        parser = self.parser
        caret = parser.caret
        if node.content_end != caret:
            return None
        pos = parser.copy_pos()
        if node.att is True:
            parser.update(node.left_b)
            parser['ElementNP'].get_attribute_list(parser, node)
        parser.update(node.final_pos)
        parser['ElementNP'].get_attribute_list(parser, node)
        del node.att
        del node.left_b
        del node.content_end
        del node.final_pos
        return pos
