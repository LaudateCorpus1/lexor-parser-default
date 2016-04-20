"""LEXOR: EVAL NodeParser

Node parser designed to hold python code to be evaluated during the converting
phase. This is a shortcut for the processing instruction: py_eval.

"""
import re
import traceback
from lexor.core.parser import NodeParser
from lexor.core.elements import (
    ProcessingInstruction, Element, CData
)

RE = re.compile('.*?[ \t\n\r\f]')


class EvalNP(NodeParser):
    """Parses content enclosed within `<%` and `%>`"""

    # noinspection PyBroadException
    def assemble_node(self, content, pos):
        """Create the processing instruction and compile it if the
        target is for python. """
        target = '?py_eval'
        node = ProcessingInstruction(target, content.strip() + '\n')
        node.set_position(*pos)
        try:
            node.compile_python(self.parser.uri, 'eval')
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
        sequence `'<%'`. If it is found it returns a `ProcessingInstruction`
        node containing all the text found till the sequence `'%>'`. If it is
        not found a warning is issued and the parser caret is updated to
        be at the end of the text that is currently begin parsed.
        """
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret + 2] != '<%':
            return None
        pos = parser.copy_pos()
        start = caret + 2
        index = parser.text.find('%>', start, parser.end)
        if index == -1:
            self.msg('E101', pos)
            content = parser.text[start:parser.end]
            parser.update(parser.end)
            return self.assemble_node(content, pos)

        content = parser.text[start:index]
        parser.update(index+2)
        return self.assemble_node(content, pos)

    def close(self, _):
        pass


MSG = {
    'E101': '`<%` was started but `%>` was not found',
    'E103': 'errors in py_eval processing instruction',
}
MSG_EXPLANATION = [
    """
    - A py_eval processing instruction may be written as
      `<% statement %>` or `<%statement%>`.

    Okay: <%a%>
    E101: <%a';
""",
    """
    - py_eval processing instructions must be valid.

    - Invalid code will be replaced with a "python_pi_error" element
      containing the traceback to help you fix the errors.

"""
]
