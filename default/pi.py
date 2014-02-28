"""LEXOR: PI NodeParser

Same as the HTML processing instruction. With the addition of
the following syntax:

    %%?PITarget PIContent%%

This means that the content cannot contain the sequence `%%`

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import ProcessingInstruction, Text

RE = re.compile('.*?[ \t\n\r\f\v]')


class ProcessingInstructionNP(NodeParser):
    """Parses content enclosed within `<?PITarget` and `?>` or
    `%%?PITarget` and `%%`. Note that the target of the
    `ProcessingInstruction` object that it returns has `?`
    preappended to it. """

    def make_node(self):
        """Returns node if the parsers caret is not position at the
        sequence `'<?'` or `'%%?'`. If it is found it returns a
        `ProcessingInstruction` node containing all the text found
        till the sequence `'?>'` or `'%%'` is found. If it is not
        found a warning is issued and the parser caret is updated to
        be at the end of the text that is currently begin parsed.

        NOTE: A valid processing instruction is of the form

            <?PITarget* or %%?PITarget*

        where `*` is a space character (this includes tabs and new
        lines).

        """
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+2] == '<?':
            shift = 1
        elif parser.text[caret:caret+3] == '%%?':
            shift = 2
        else:
            return None
        pos = parser.copy_pos()
        match = RE.search(parser.text, caret+shift)
        if match:
            target = parser.text[parser.caret+shift:match.end(0)-1]
        else:
            self.msg('E100', pos)
            content = parser.text[parser.caret:parser.end]
            parser.update(parser.end)
            return Text(content)
        if shift == 1:
            index = parser.text.find('?>', match.end(0), parser.end)
            if index == -1:
                self.msg('E101', pos, [target])
                content = parser.text[match.end(0):parser.end]
                parser.update(parser.end)
                return ProcessingInstruction(target, content)
        else:
            index = parser.text.find('%%', match.end(0), parser.end)
            if index == -1:
                content = parser.text[match.end(0):parser.end]
                parser.update(parser.end)
                self.msg('E102', pos, [target])
                return ProcessingInstruction(target, content)
        content = parser.text[match.end(0):index]
        parser.update(index+2)
        return ProcessingInstruction(target, content)


MSG = {
    'E100': 'ignoring processing instruction',
    'E101': '`<{0}` was started but `?>` was not found',
    'E102': '`%%{0}` was started but `%%` was not found',
}
MSG_EXPLANATION = [
    """
    - A processing instruction must have a target and must be
      enclosed within `<?` and `?>`.

    - If there is no space following the target of the processing
      instruction, that is, if the file ends abrutly, then the
      processing instruction will be ignored.

    Okay: <?php echo '<p>Hello World</p>'; ?>
    Okay: %%?python print '<p>Hello World</p>' %%

    E100: <?php
    E101: <?php echo '<p>Hello World</p>';
    E102: %%?python print '<p>Hello World</p>'
""",
]
