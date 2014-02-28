"""LEXOR: CODE NodeParser

"""
from lexor.core.parser import NodeParser
from lexor.core.elements import Element, Text


class CodeInlineNP(NodeParser):
    """Obtain code enclosed by backticks. """

    @staticmethod
    def build_node(parser, content):
        """Build the actual node with the given content. """
        node = Element('code')
        node.append_child(Text(content))
        parser['ElementNP'].get_attribute_list(parser, node)
        return [node]

    def obtain_content(self, parser, index, end_index, count):
        """Check for a possible ambiguity and return the
        content of the inline code node. """
        ambiguous = False
        try:
            if parser.text[end_index+count] == '`':
                ambiguous = True
                while parser.text[end_index+count] == '`':
                    end_index += 1
        except IndexError:
            pass
        if ambiguous:
            self.msg('E100', parser.pos, parser.compute(end_index))
        parser.update(end_index+count)
        content = parser.text[index:end_index].strip()
        if not content:
            content = ' '
        return content

    def make_node(self):
        parser = self.parser
        if parser.text[parser.caret] != '`':
            return None
        count = 1
        index = parser.caret + 1
        try:
            while parser.text[index] == '`':
                count += 1
                index += 1
        except IndexError:
            index += 1
        total = count
        end_index = parser.text.find('`'*count, index, parser.end)
        if end_index != -1:
            content = self.obtain_content(parser, index, end_index, count)
            return self.build_node(parser, content)
        start = index
        while count > 0:
            end_index = parser.text.find('`'*count, index, parser.end)
            if end_index > 0:
                pos = parser.compute(end_index)
                self.msg('E100', parser.pos, pos)
                parser.update(end_index+count)
                content = parser.text[start:end_index].strip()
                return self.build_node(parser, content)
            count -= 1
            start -= 1
        pos = parser.compute(parser.caret+total)
        self.msg('E101', parser.pos, pos)
        parser.update(parser.caret+total)
        return Text('`'*(total))


MSG = {
    'E100': 'ambiguous inline code ends at {0}:{1:2}',
    'E101': 'no more backticks after {0}:{1:2} to match',
}
MSG_EXPLANATION = [
    """
    - Inline code can be marked up by surrounding it with backticks.
      To use literal backticks, use two or more backticks as
      delimiters.

    - When inserting literal backticks you should use a space right
      after the starting delimiter and one space right before the
      closing delimiter. This rule is to avoid ambiguity.

    Okay:
        `a < b`

    Okay:
        Use backticks to markup code, e.g. `` `code` ``.

    Okay:
        This is a backtick: `` ` ``.

    E100:
        This is a backtick: `` ```.

    E100:
        This is a backtick: ``` ``.

    E101:
        This is a backtick: `````.
""",
]
