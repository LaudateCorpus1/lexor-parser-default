"""LEXOR: DOCTYPE NodeParser

DOCTYPE is case insensitive in HTML. The following forms are valid:

    <!doctype html>
    <!DOCTYPE html>
    <!DOCTYPE HTML>
    <!DoCtYpE hTmL>

New Form:

    %%!doctype html%%
    %%!DOCTYPE html%%
    %%!DOCTYPE HTML%%
    %%!DoCtYpE hTmL%%

See: http://stackoverflow.com/a/9109157/788553

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import DocumentType

class DocumentTypeNP(NodeParser):
    """Reads the doctype tag. """

    def _regular_doctype(self, parser, caret):
        """Parse regular doctype. """
        char = parser.text[caret+9:caret+10]
        if char not in ' \t\n\r\f\v':
            return None
        index = parser.text.find('>', caret+10)
        if index == -1:
            self.msg('E100', parser.pos, ['>'])
            parser.update(parser.end)
            return DocumentType(parser.text[caret+10:parser.end])
        parser.update(index+1)
        return DocumentType(parser.text[caret+10:index])

    def _new_doctype(self, parser, caret):
        """Parse new doctype. """
        char = parser.text[caret+10:caret+11]
        if char not in ' \t\n\r\f\v':
            return None
        index = parser.text.find('%%', caret+11)
        if index == -1:
            self.msg('E100', parser.pos, ['%%'])
            parser.update(parser.end)
            return DocumentType(parser.text[caret+11:parser.end])
        parser.update(index+2)
        return DocumentType(parser.text[caret+11:index])

    def make_node(self):
        """Returns a DocumentType node. """
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+9].lower() == '<!doctype':
            return self._regular_doctype(parser, caret)
        if parser.text[caret:caret+10].lower() == '%%!doctype':
            return self._new_doctype(parser, caret)
        return None


MSG = {
    'E100': '`{0}` not found',
}
MSG_EXPLANATION = [
    """
    - A `doctype` element starts with `<!doctype` and it is
      terminated by `>`.

    Okay: <!doctype html>
    Okay: <!DOCTYPE html>
    Okay: %%!doctype html%%
    Okay: %%!DOCTYPE html%%

    E100: <!doctype html
    E100: %%!doctype html
""",
]