"""LEXOR: CODE NodeParser

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Element, Text
LANG_RE = re.compile(r'''
    (?:(?:^::+)|(?P<shebang>^[#]!)) # Shebang or 2 or more colons.
    (?P<path>(?:/\w+)*[/ ])?        # Zero or 1 path
    (?P<lang>[\w+-]*)               # The language
    ''', re.VERBOSE)
FENCED = re.compile(r'\n~{3,}[~]+[ ]*(\n|$)')


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


def code_hilite(line_one, node):
    """This function is a modification from CodeHilite.py created by
    Waylan Limberg.

    It determines the language of the code block from the first line
    and whether said line should be removed or left in place. If the
    shebang line contains a path (even a single /) then it is assumed
    to be a real shebang line and left alone. However, if no path is
    given (e.i.: #!python or :::python) then it is assumed to be a
    mock shebang for language identifitation of a code fragment and
    removed from the code block prior to processing for code
    highlighting. When a mock shebang (e.i: #!python) is found, line
    numbering is turned on. When colons are found in place of a
    shebang (e.i.: :::python), line numbering is left off. More info
    here:

    http://packages.python.org/Markdown/extensions/code_hilite.html

    In addition, the information on the first line will set the class
    attribute of the node so that it may work with SyntaxHighlighter
    developed by Alex Gorbatchev. More info here:

    http://alexgorbatchev.com/SyntaxHighlighter

    After the shebang line you may write more instructions that for
    the syntaxHighliter. For instance:

    #!/usr/bin/python first-line: 10; highlight: [2, 4, 6]

    Everything after the first space will be appened to the class
    attribute. For this reason there is no need to modify the
    attribute list which can be declared in the first line.

    #!/usr/bin/python highlight: [2, 4, 6] {#someid}

    If you wish to overwrite the class attribute completely then you
    may start with the following line:

    :::{class="new"}

    Note that doing so will also result in lexor giving you a warning
    since you overwriting an attribute which has already been
    declared.

    The function returns either an empty list or a list with the first
    line as its only element."""
    block = list()
    head = line_one.split(' ', 1)
    match = LANG_RE.search(head[0])
    if match:
        try:
            node['class'] = 'brush: %s;' % match.group('lang').lower()
        except IndexError:
            node['class'] = 'brush: plain;'
        if match.group('path'):
            block.append(head[0])
        if match.group('shebang'):
            node['class'] += ' gutter: true;'
        else:
            node['class'] += ' gutter: false;'
        if len(head) > 1:
            node['class'] += (' ' + head[1]).rstrip()
    else:
        block.append(line_one)
        node['class'] = 'brush: plain; gutter: false;'
    return block


class CodeBlockNP(NodeParser):
    """A code block is a block that stars with a line with 4 spaces
    or the tab character. The block ends when the line does not start
    with 4 spaces or a tab character.

    You may also start a code block by writing a sequence of three
    `~` at the beginning of the line, in this way there no
    indentation will be required. The block ends with a row of `~` at
    least as long as the starting row.

    This returns a pre tag to work with Alex Gorbatchev's
    [SyntaxHighlighter](http://alexgorbatchev.com/SyntaxHighlighter)

    This function uses the code_hilite function which is a modified
    body of code from Waylan Limberg. See the documentation on
    code_hilite for more info.

    Note that this does not replace the characters '<' and '&'. The
    writer must convert these characters in the output."""

    def get_fenced_block(self, match):
        """Parse a fenced block code. """
        parser = self.parser
        text = parser.text
        total = text[match.start()+1:match.end()].count('~')
        parser.update(match.end())
        node = Element('codeblock')

        index = parser.text.find('\n', parser.caret)
        if index == -1:
            index = parser.end
        left_b = parser.text.find('{', parser.caret, index)
        if left_b != -1:
            line = parser.text[parser.caret:left_b]
        else:
            line = parser.text[parser.caret:index]

        block = code_hilite(line, node)
        if block:
            append = block[0] + '\n'
        else:
            append = ''

        if left_b != -1:
            parser.update(left_b)
            self.parser['ElementNP'].get_attribute_list(parser, node)
            if text[parser.caret] == '\n':
                parser.update(parser.caret+1)
        else:
            parser.update(index+1)

        rfenced = re.compile(r'\n~{'+str(total-1)+',}[~]+[ ]*(\n|$)')
        match = rfenced.search(text, parser.caret)
        if not match:
            self.msg('E200', parser.pos, [total])
            node.append_child(append+text[parser.caret:])
            parser.update(parser.end)
            return [node]
        node.append_child(append+text[parser.caret:match.start()])
        parser.update(match.end())
        return [node]

    def make_node(self):
        parser = self.parser
        match = FENCED.match(parser.text, parser.caret-1)
        if match:
            return self.get_fenced_block(match)
        text = self.parser.text[parser.caret:parser.caret+4]
        if text != 4*' ' and text[0:1] != '\t':
            return None
        node = Element('codeblock')

        index = parser.text.find('\n', parser.caret, parser.end)
        if index == -1:
            index = parser.end
        left_b = parser.text.find('{', parser.caret, index)
        if left_b != -1:
            line = parser.text[parser.caret:left_b]
        else:
            line = parser.text[parser.caret:index]
        line_one = line[1:] if line[0:1] == '\t' else line[4:]

        block = code_hilite(line_one, node)

        if left_b != -1:
            parser.update(left_b)
            self.parser['ElementNP'].get_attribute_list(parser, node)

        while index < parser.end:
            old_index = index + 1
            index = parser.text.find('\n', old_index, parser.end)
            if index == -1:
                index = parser.end
            line = parser.text[old_index:index]
            if line[0:4] == 4*' ':
                block.append(line[4:])
            elif line[0:1] == '\t':
                block.append(line[1:])
            else:
                index = index + 1
                break
        node.append_child(Text('\n'.join(block)))
        parser.update(index)
        return [node]


MSG = {
    'E100': 'ambiguous inline code ends at {0}:{1:2}',
    'E101': 'no more backticks after {0}:{1:2} to match',
    'E200': 'closing row of `{0}` or more `~` not found',
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
""", """
    - Fenced code blocks start with 4 or more `~`. To close it you
      must end the block with at least the number of `~` of the
      starting row.

    Okay:
        ~~~~
        print 'hello'
        ~~~~

    Okay:
        ~~~~~~~
        ~~~~
        print 'hello'
        ~~~~
        ~~~~~~~

    E200:
        ~~~~~~~
        ~~~~
        print 'hello'
        ~~~~
        ~~~~~~
""",
]
