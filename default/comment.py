"""LEXOR: COMMENT NodeParser

Comments as in HTML are enclosed within `<!--` and `-->`. The string
`--` (double-hyphen) MUST NOT occur within comments. Unlike the HTML
parser the comment may start with `<!`. Another form of comment is
enclosed within `%%!` and `%%`. If the last form is used then the
comment may not contain the string '%%'.

See: http://www.w3.org/TR/REC-xml/#sec-comments

"""

from lexor.core.parser import NodeParser
from lexor.core.writer import replace
from lexor.core.elements import Comment


class CommentNP(NodeParser):
    """Lexor comment parser. """

    def _regular_comment(self, parser, caret):
        """Parse regular comments. """
        if parser.text[caret+2:caret+4] != '--':
            index = parser.text.find('>', caret+2)
            if index == -1:
                self.msg('E100', parser.pos)
                parser.update(parser.end)
                content = parser.text[caret+2:parser.end]
                return Comment(replace(content, ('--', '- ')))
            parser.update(index+1)
            content = replace(parser.text[caret+2:index], ('--', '- '))
            return Comment(content)
        index = parser.text.find('--', caret+4)
        if index == -1:
            self.msg('E200', parser.pos)
            parser.update(parser.end)
            return Comment(parser.text[caret+4:parser.end])
        content = parser.text[caret+4:index]
        while parser.text[index:index+3] != '-->':
            content += '- '
            newindex = parser.text.find('--', index+1)
            if newindex == -1:
                content += parser.text[index+2:parser.end]
                self.msg('E200', parser.pos)
                parser.update(parser.end)
                return Comment(content)
            content += parser.text[index+2:newindex]
            index = newindex
        parser.update(index+3)
        return Comment(content)

    def _new_comment(self, parser, caret):
        """parse new style comment. """
        index = parser.text.find('%%', caret+3)
        if index == -1:
            self.msg('E100', parser.pos)
            parser.update(parser.end)
            return Comment(parser.text[caret+3:parser.end])
        content = parser.text[caret+3:index]
        parser.update(index+3)
        return Comment(replace(content, ('--', '- ')))

    def make_node(self):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+2] == '<!':
            return self._regular_comment(parser, caret)
        elif parser.text[caret:caret+3] == '%%!':
            return self._new_comment(parser, caret)
        return None


MSG = {
    'E100': 'comment closing delimiter not found',
    'E200': '`-->` not found',
}
MSG_EXPLANATION = [
    """
    - A comment started with `<!--` must end with `-->`. If the
      comment started with `<!` then you are only required to finish
      it with `>`. Note that in this case your comment cannot contain
      the greater than sign.

    - A comment started with `%%!` must end with `%%`. In this case
      you cannot write `%%` inside the comment.

    Okay: <!--simple comment-->
    Okay: <!simple comment>
    Okay: %%!simple comment%%

    E100: <!simple comment
    E100: <!simple comment%%
    E100: %%!simple comment
    E200: <!--simple comment>
""",
]
