"""LEXOR: ELEMENT NodeParser

Handles all `Elements` in the form

    <tagname att1="val1" att2="val2">...</tagname>
    <tagname #id .class1>...</tagname>
    %%{tagname id="id" class="class1"}...%%
    %%{tagname #id .class1}...%%
    %%{#id .class1}...%%

If no tagname is given then it the name of the element defaults to
`span`.

"""

import re
from lexor.util import Position
from lexor.core.parser import NodeParser
from lexor.core.elements import Element, Void, RawText

RE = re.compile(r'.*?[ \t\n\r\f\v/>}]')
RE_NOSPACE = re.compile(r"\s*")
RE_NEXT = re.compile(r'.*?[ \t\n\r\f\v/>=]')
VOID_ELEMENT = (
    'area', 'base', 'basefont', 'br', 'col', 'frame', 'hr', 'img',
    'input', 'isindex', 'link', 'meta', 'param', 'command', 'embed',
    'keygen', 'source', 'track', 'wbr', 'include', 'documentclass',
    'bibliography',
)
RAWTEXT_ELEMENT = (
    'script', 'style', 'textarea', 'title', 'undef', 'usepackage',
)
AUTO_CLOSE = {
    'p': [
        'address', 'article', 'aside', 'blockquote', 'dir', 'div',
        'dl', 'fieldset', 'footer', 'form', 'h1', 'h2', 'h3', 'h4',
        'h5', 'h6', 'header', 'hgroup', 'hr', 'main', 'menu', 'nav',
        'ol', 'p', 'pre', 'section', 'table', 'ul',
    ],
    'a': [
        'a'
    ]
}
AUTO_CLOSE_FIRST = {
    'li': ['li'],
    'dt': ['dt', 'dd'],
    'dd': ['dt', 'dd'],
    'rt': ['rt', 'rp'],
    'rp': ['rt', 'rp'],
    'optgroup': ['optgroup'],
    'option': ['optgroup', 'option'],
    'thead': ['tbody', 'tfoot'],
    'tbody': ['tbody', 'tfoot'],
    'tfoot': ['tbody'],
    'tr': ['tr'],
    'td': ['td', 'th'],
    'th': ['td', 'th']
}
END_CHAR = {
    '<': '>',
    '%%{': '}',
    1: '>',
    3: '}'
}


class ElementNP(NodeParser):
    """Parses all the lexor elements. The following are equivalent
    elements:

        <div id="id" class="class1">div content</div>
        <div #id .class1>div content</div>
        %%{div id="id" class="class1"}div content%%
        %%{div #id .class1}div content%%

    The following form declares a `span` tag:

        %%{#id .class1}div content%%

    This is using the default form of this new tag format. There are
    cases when span elements are useful when formatting and we need
    to either give them a class or id. The following is a an empty
    span

        %%{}%%

    The start tag is '%%{}' Inside the brackets we can put the
    nametag and attributes. The tag ends when '%%' is encountered.
    Using this form allows also to put the old html tag format as
    well as the new one.

    The rules of HTML apply here. For instance if you write a "p" tag
    it and we encounter another "p" tag before its closing tag then
    the first p tag will be closed."""

    def is_element(self, parser):
        """Check to see if the parser's caret is positioned in an
        element and return the index where the opening tag ends and
        the number 1 (if element starts with '<') or 3 (if it starts
        with '%%{'). """
        caret = parser.caret
        search = False
        if parser.text[caret:caret+1] == '<':
            shift = 1
        elif parser.text[caret:caret+3] == '%%{':
            shift = 3
            if parser.text[caret+3:caret+4] == '}':
                return [caret+4, shift]
            if parser.text[caret+3:caret+4] in '.#@[':
                search = True
        else:
            return None
        char = parser.text[caret+shift:caret+shift+1]
        if search or char.isalpha() or char in [":", "_"]:
            endindex = parser.text.find(END_CHAR[shift], caret+shift)
            if endindex == -1:
                return None
            start = parser.text.find('<', caret+1)
            if start != -1 and start < endindex:
                pos = parser.compute(start)
                self.msg('E100', parser.pos, [Position(pos)])
                return None
        else:
            return None
        return [endindex, shift]

    def get_tagname(self, parser):
        """If the parser is positioned at an element it will return
        the tagname, otherwise it returns None. """
        caret = parser.caret
        tmp = self.is_element(parser)
        if tmp is None:
            return None
        shift = tmp[1]
        match = RE.search(parser.text, caret+shift)
        tagname = parser.text[parser.caret+shift:match.end(0)-1]
        if tagname == '' or tagname[0] in '.#[@':
            tagname = 'span'
        return tagname.lower()

    def get_raw_text(self, parser, tagname, pos, shift):
        """Return the data content of the RawText object and update
        the caret. """
        if shift == 3:
            start, end = '%%{', '%%'
            index = parser.text.find('%%', parser.caret)
        else:
            start, end = '<', ('</%s>' % tagname)
            index = parser.text.find('<', parser.caret)
            while index != -1:
                tmpstr = parser.text[index:index+len(tagname)+3].lower()
                if tmpstr == end:
                    break
                index = parser.text.find('<', index+1)
        if index == -1:
            self.msg('E110', pos, [start, tagname, end])
            content = parser.text[parser.caret:]
            parser.update(parser.end)
        else:
            content = parser.text[parser.caret:index]
            parser.update(index+len(end))
        return content

    def is_done(self, node, parser, caret):
        """Checks to see if the node should be closed. It returns one
        of 3 values: None, pos, False. The value of False means that
        the node is not yet done and that further checks need to be
        performed. """
        flag = None
        if node.type__ == 1:
            if parser.text[caret:caret+1] != '<':
                pass
            elif parser.text[caret+1:caret+2] == '/':
                index = parser.text.find('>', caret+2)
                if index == -1:
                    return None
                tmptag = parser.text[caret+2:index].lower()
                if node.name == tmptag:
                    pos = parser.copy_pos()
                    parser.update(index+1)
                    return pos
            else:
                flag = self.is_element(parser)
        elif node.type__ == 3:
            if parser.text[caret:caret+3] in ['%%?', '%%!']:
                return None
            flag = self.is_element(parser)
            if flag:
                pass
            elif parser.text[caret:caret+2] == '%%':
                pos = parser.copy_pos()
                parser.update(caret+2)
                return pos
        if flag is None:
            return None
        return False

    def make_node(self):
        """Returns an `Element` node. """
        parser = self.parser
        caret = parser.caret
        tmp = self.is_element(parser)
        if tmp is None:
            return None
        endindex = tmp[0]
        shift = tmp[1]
        pos = parser.copy_pos()
        match = RE.search(parser.text, caret+shift)
        tagname = parser.text[parser.caret+shift:match.end(0)-1].lower()
        if tagname == '' or tagname[0] in '.#!@':
            tagname = 'span'
            parser.update(caret+3)
        else:
            parser.update(match.end(0)-1)
        if tagname in VOID_ELEMENT:
            node = Void(tagname)
        elif tagname in RAWTEXT_ELEMENT:
            node = RawText(tagname)
        else:
            node = Element(tagname)
        if parser.text[parser.caret] == END_CHAR[shift]:
            parser.update(parser.caret+1)
        elif parser.text[parser.caret] == '/':
            parser.update(endindex+1)
        else:
            self.read_attributes(parser, node, endindex)
        if isinstance(node, Void):
            return [node]
        if isinstance(node, RawText):
            node.data = self.get_raw_text(parser, tagname, pos, shift)
            return [node]
        node.pos = pos
        node.type__ = shift
        return node

    def close(self, node):
        """Returns the position where the element was closed. """
        parser = self.parser
        caret = parser.caret
        done = self.is_done(node, parser, caret)
        if isinstance(done, list):
            del node.type__
            return done
        if done is None:
            return done
        # http://www.whatwg.org/specs/web-apps/current-work/#optional-tags
        match = RE.search(parser.text, caret+node.type__)
        if parser.text[parser.caret] == '<':
            tmptag = parser.text[parser.caret+1:match.end(0)-1].lower()
        else:
            tmptag = parser.text[parser.caret+3:match.end(0)-1].lower()
        if node.name in AUTO_CLOSE and tmptag in AUTO_CLOSE[node.name]:
            del node.type__
            return parser.copy_pos()
        if node.name in AUTO_CLOSE_FIRST:
            has_element = False
            for child in node.child:
                if isinstance(child, Element):
                    has_element = True
                    break
            if has_element is False and tmptag in AUTO_CLOSE_FIRST[node.name]:
                del node.type__
                return parser.copy_pos()
        return None

    def is_empty(self, parser, index, end, tagname):
        """Checks to see if the parser has reached '/'. """
        if parser.text[index] == '/':
            parser.update(end+1)
            if end - index > 1:
                self.msg('E120', parser.compute(index))
            if tagname not in VOID_ELEMENT:
                self.msg('E121', parser.compute(index))
            return True
        return False

    def read_prop(self, parser, node, end, attlen):
        """Return [prop, prop_index, implied, empty]. """
        prop = None
        prop_index = None
        match = RE_NOSPACE.search(parser.text, parser.caret, end)
        if self.is_empty(parser, match.end(0), end, node.name):
            return prop, prop_index, False, True
        if parser.text[match.end(0)] in '>}':
            parser.update(end+1)
            return prop, prop_index, False, False
        prop_index = match.end(0)
        if prop_index - parser.caret == 0 and node.attlen > attlen:
            self.msg('E130', parser.pos)
        match = RE_NEXT.search(parser.text, prop_index, end)
        if match is None:
            prop = parser.text[prop_index:end]
            parser.update(end+1)
            return prop, prop_index, True, False
        prop = parser.text[prop_index:match.end(0)-1]
        if self.is_empty(parser, match.end(0)-1, end, node.name):
            return prop, prop_index, True, True
        if parser.text[match.end(0)-1] == '=':
            parser.update(match.end(0))
            return prop, prop_index, False, False
        match = RE_NOSPACE.search(parser.text, match.end(0), end)
        if parser.text[match.end(0)] == '=':
            implied = False
            parser.update(match.end(0)+1)
        else:
            implied = True
            parser.update(match.end(0)-1)
        return prop, prop_index, implied, False

    def read_val(self, parser, end, tagname):
        """Returns the attribute value. """
        match = RE_NOSPACE.search(parser.text, parser.caret, end)
        if self.is_empty(parser, match.end(0), end, tagname):
            return ''
        if parser.text[match.end(0)] in '>}':
            parser.update(end+1)
            return ''
        val_index = match.end(0)
        if parser.text[val_index] in ["'", '"']:
            quote = parser.text[val_index]
            index = parser.text.find(quote, val_index+1, end)
            if index == -1:
                pos = parser.compute(end)
                self.msg('E150', parser.pos, [Position(pos)])
                parser.update(end+1)
                return parser.text[val_index+1:end]
            parser.update(index+1)
            return parser.text[val_index+1:index]
        else:
            pos = parser.copy_pos()
            match = RE.search(parser.text, val_index, end)
            if match is None:
                val = parser.text[val_index:end]
                for item in '\'"=':
                    if item in val:
                        self.msg('E140', pos, [item])
                parser.update(end+1)
                return val
            if parser.text[match.end(0)-1] == '/':
                self.msg('E141', pos)
                parser.update(match.end(0)-1)
            else:
                parser.update(match.end(0)-1)
            val = parser.text[val_index:match.end(0)-1]
            for item in '\'"=':
                if item in val:
                    self.msg('E140', pos, [item])
            return val

    #pylint: disable=R0913
    def handle_id_ref(self, parser, node, prop, prop_index, prop_type):
        """Handle the ID and Python references. """
        mapping = {
            'id': 'element IDs',
            '_pyref': 'python references',
            '#': '@',
            '@': '#',
        }
        if len(prop) == 1:
            self.msg(
                'E170', parser.compute(prop_index), [mapping[prop_type]]
            )
        elif prop[-1] == mapping[prop[0]]:
            val = prop[1:-1]
            if len(val) > 0:
                node['_pyref'] = val
                node['id'] = val
            else:
                self.msg('E171', parser.compute(prop_index))
        else:
            node[prop_type] = prop[1:]

    def prop_shortcut(self, parser, node, prop, prop_index):
        """Instead of having an implied attribute we may have one of
        the following shortcuts:

            #idname .class1 [attref1] @ref

        The first sets the attribute id to idname. If the implied
        value starts with a period (dot) then that value gets
        appended to the attribute class. If the values are within
        square brackets then the content of the brackets gets
        appended to an attribute called _alref. The valid If the
        value starts with @ then its value will be stored in an
        attribute called _pyref. Notice that the value cannot be
        empty.

        There are two extra shortcuts which are derived from # and @.
        The following are equivalent: #id-ref-name@ and
        @id-ref-name#. The first expression says that the id should
        be "id-ref-name" and that the same name should be used for
        python to store the reference. The second one says to use
        "id-ref-name" for python to store the reference and to use
        the same name as the id. """
        if prop[0] == '@':
            self.handle_id_ref(parser, node, prop, prop_index, '_pyref')
        elif prop[0] == '#':
            self.handle_id_ref(parser, node, prop, prop_index, 'id')
        elif prop == 'id':
            self.msg(
                'E170', parser.compute(prop_index), ['element IDs']
            )
        elif prop[0] == '.':
            if 'class' in node:
                node['class'] += ' %s' % prop[1:]
            else:
                node['class'] = prop[1:]
        elif prop[0] == '[' and prop[-1] == ']':
            val = prop[1:-1].lower()
            if '_alref' in node:
                node['_alref'].append((parser.compute(prop_index), val))
            else:
                node['_alref'] = [(parser.compute(prop_index), val)]
        else:
            node[prop] = ""

    def read_attributes(self, parser, node, end, skip=1):
        """Parses the string

            parser.text[parser.caret:end]

        and writes the information in node.

            att1="val1" att2="val2" ...

        This function returns True if the opening tag ends with `/`.
        """
        attlen = node.attlen
        while parser.caret < end:
            prop, prop_index, implied, empty = self.read_prop(
                parser, node, end, attlen
            )
            if prop is None or prop == '':
                parser.update(end+skip)
                return empty
            if prop in node:
                self.msg('E160', parser.compute(prop_index), [prop])
            if implied is True:
                self.prop_shortcut(parser, node, prop, prop_index)
                if empty is True:
                    parser.update(end+skip)
                    return empty
            else:
                val = self.read_val(parser, end, node.name)
                node[prop] = val
        parser.update(end+skip)

    def get_attribute_list(self, parser, node, start='{', end='}'):
        """Attempts to get the attribute list at the current position
        where the parser is reading. """
        caret = parser.caret
        if parser.text[caret:caret+1] != start:
            return None
        index = parser.text.find(end, caret, parser.end)
        if index == -1:
            return None
        parser.update(parser.caret+1)
        self.read_attributes(parser, node, index)


MSG = {
    'E100': 'element discarded due to `<` at {0}',
    'E110': '`RawText` {0}{1} closing tag `{2}` not found',
    'E120': '`/` not immediately followed by `>`',
    'E121': 'self-closing syntax (`/>`) used in non-void element',
    'E130': 'no space between attributes',
    'E140': '`{0}` found in unquoted attribute value',
    'E141': '`/` found in unquoted attribute value',
    'E150': 'assuming quoted attribute to close at {0}',
    'E160': 'attribute name "{0}" has already been declared',
    'E170': '{0} cannot be empty',
    'E171': 'python references and element ids cannot be empty',
}
MSG_EXPLANATION = [
    """
    - The opening tag of an element cannot contain `<`. This means
      that attributes cannot contain `<` in them.

    Okay: <apple att1="val1"></apple>

    E100: <apple att1="a < b"></apple>
""",
    """
    - `RawText` elements are terminated when the appropriate closing
      tag is found. Make sure to provide its proper closing tag.

    Okay: <title>My awesome website</title>
    Okay: %%{title}My awesome website%%
    Okay: <script>a < b && b > c</script>
    Okay: %%{script}a < b && b > c%%

    E110: <title>My not so great website</title >
    E110: <title>My not so great website< / title >
    E110: <title>My not so great website
    E110: <script>a < b && b > c
    E110: %%{script}a < b && b > c%
    E110: %%{script}a < b && b > c
""",
    """
    - A `Void` Element's opening tag must end with `/>`. Anything in
      between the characters `/` and `>` will be ignored.

    - Non-void elements whose opening tag start with `/>` will be
      also be interpreted correctly a message will be issued.

    Okay:
        <img href="/path/to/image.png"/>

    Okay: <p>starting a new paragraph</p>

    E120: <img href="/path/to/image.png"/  >
    E121: <p />starting a new paragraph</p>
""",
    """
    - Attributes need to be separated by one space.

    - Do not repeat attributes since the values will only get
      overwritten.

    Okay: <tag att1="val1" att2="val2">content</tag>
    Okay: <tag att1='1' att2='2'></tag>

    E130: <tag att1="val1"att2="val2">content</tag>
    E160: <tag att1='1' att1='2'></tag>
""",
    """
    A few attributes rules:

    - There is a risk of joining attributes together when using
      unquoted attribute values. This may result in having a quote or
      equal sign inside the unquoted attribute value. [E140]

    - If your attribute contains `/` then the attribute should be
      quoted. [E141]

    - Quoted attributes need to be finished by its starting quotation
      character. [E150]

    Okay: <tag att1=val1 att2="val2">content</tag>
    E140: <tag att1=val1att2="val2">content</tag>
    Okay: <tag @idname .class1 .class2 [attref1] @ref>content</tag>

    Okay:
        %%{img href="path/to/image.png"}

    E141:
        <img href=path/to/image.png />

    Okay: <tag att1="num"></tag>
    Okay: <tag att1='num'></tag>

    E150: <tag att1="num'></tag>
    E150: <tag att1="num></tag>
    E150: <tag att1='num"></tag>
    E150: <tag att1='num></tag>
""",
    """
    - The id attribute need to begin with a letter ([A-Za-z]) and may
      be followed by any number of letters, digits ([0-9]), hyphens
      (`-`), underscores (`_`), colons (`:`), and periods (`.`).

    - The `@` symbol is reserved to tell python that you wish to
      keep a reference to that particular element.

    Okay: %%{h1 #section-1}Section 1%%
    Okay: <h2 #section-2 @sec2>Section 2</h2>
    Okay: %%{h3 #sec3@}Section 3%%

    E170: %%{h1 #}Section 1%%
    E170: <h2 #section-2 @>Section 2</h2>
    E170: %%{h1 id}Section 1%%
    E171: %%{h3 #@}Section 3%%
""",
]
