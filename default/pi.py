"""LEXOR: PI NodeParser

Same as the HTML processing instruction. With the addition of
the following syntax:

    %%?PITarget PIContent%%

This means that the content cannot contain the sequence `%%`

"""
import re
import traceback
from lexor.core.parser import NodeParser
from lexor.core.elements import (
    ProcessingInstruction, Text, Element, CData
)

RE = re.compile('.*?[ \t\n\r\f]')


class ProcessingInstructionNP(NodeParser):
    """Parses content enclosed within `<?PITarget` and `?>` or
    `%%?PITarget` and `%%`. Note that the target of the
    `ProcessingInstruction` object that it returns has `?`
    prepended to it.
    """

    # noinspection PyBroadException
    def assemble_node(self, target, content, pos):
        """Create the processing instruction and compile it if the
        target is for python. """
        node = ProcessingInstruction(target, content)
        node.set_position(*pos)
        if target in ['?py', '?python', '?py_eval']:
            try:
                mode = 'eval' if target == '?py_eval' else 'exec'
                node.compile_python(self.parser.uri, mode)
            except BaseException:
                self.msg('E103', pos)
                err_node = Element('python_pi_error')
                err_node.set_position(*pos)
                err_data = CData(traceback.format_exc())
                err_data.set_position(pos[0], pos[1]+1+len(target))
                err_node.append_child(
                    err_data
                )
                return [err_node]
        return node

    def make_node(self):
        """Returns None if the parsers caret is not positioned at the
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
        start = match.end(0) - 1
        if parser.text[start] in [' ', '\t']:
            start += 1
        if shift == 1:
            index = parser.text.find('?>', match.end(0), parser.end)
            if index == -1:
                self.msg('E101', pos, [target])
                content = parser.text[start:parser.end]
                parser.update(parser.end)
                return self.assemble_node(target, content, pos)
        else:
            index = parser.text.find('%%', match.end(0), parser.end)
            if index == -1:
                self.msg('E102', pos, [target])
                content = parser.text[start:parser.end]
                parser.update(parser.end)
                return self.assemble_node(target, content, pos)
        content = parser.text[start:index]
        parser.update(index+2)
        return self.assemble_node(target, content, pos)

    def close(self, _):
        pass


MSG = {
    'E100': 'ignoring processing instruction',
    'E101': '`<{0}` was started but `?>` was not found',
    'E102': '`%%{0}` was started but `%%` was not found',
    'E103': 'errors in python processing instruction',
}
MSG_EXPLANATION = [
    """
    - A processing instruction must have a target and must be
      enclosed within `<?` and `?>`.

    - If there is no space following the target of the processing
      instruction, that is, if the file ends abruptly, then the
      processing instruction will be ignored.

    Okay: <?php echo '<p>Hello World</p>'; ?>
    Okay: %%?python print '<p>Hello World</p>' %%

    E100: <?php
    E101: <?php echo '<p>Hello World</p>';
    E102: %%?python print '<p>Hello World</p>'
""",
    """
    - Python processing instructions must be valid.

    - Invalid code will be replaced with a "python_pi_error" element
      containing the traceback to help you fix the errors.

    Okay: <?py print 'hello world' ?>

    E103: <?py print 'hello world ?>
    E103:
        <?python
        for i in xrange(5)
            print 'hello'
        ?>

"""
]
