"""LEXOR: DEFINE NodeParser

Node parser description.

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Void
from collections import OrderedDict

RE = re.compile(r'\s+')


class MacroNP(NodeParser):
    """Parse elements inside the define block. """

    def get_function(self, pos, exp):
        """Obtain the function name. """
        index = exp.find('{')
        if index == -1:
            self.msg('E101', pos, ['{'])
        name = exp[:index]
        if exp[-1] != '}':
            self.msg('E101', pos, ['}'])
        tmp = exp[index+1:-1].split(',')
        tmp = [item.split(':') for item in tmp]
        arg = OrderedDict()
        for item in tmp:
            if len(item) == 2:
                arg[item[0]] = item[1]
            else:
                arg[item[0]] = ''
        return name, arg

    def make_node(self):
        parser = self.parser
        if parser.text[parser.caret:parser.caret+3] == '\n%%':
            return None
        index = parser.text.find('\n', parser.caret+1)
        while index != -1:
            if parser.text[index-1] == '\\':
                index = parser.text.find('\n', index+1)
            else:
                break
        if index == -1:
            parser.update(parser.caret+1)
            return None

        pos = parser.compute(parser.caret+1)
        content = parser.text[parser.caret:index].strip()
        parser.update(index)

        flag = 'set_delayed'
        index = content.find(':=')
        if index == -1:
            flag = 'set'
            index = content.find('=')
            if index == -1:
                self.msg('E100', pos)
                node = Void('macro', {'flag': 'failed'})
                return node

        name = content[:index].strip()
        if name[0] == '\\':
            name, arg = self.get_function(pos, name)

        if flag == 'set':
            value = content[index+1:]
        else:
            value = content[index+2:]
        value = re.sub(RE, ' ', value.strip().replace('\\\n', ''))

        node = Void('macro')
        node['flag'] = flag
        node['name'] = name
        node['value'] = value
        if name[0] == '\\':
            node['arg'] = arg
        return node


MSG = {
    'E100': 'no `=` or `:=` found in macro declaration',
    'E101': 'missing `{0}` in macro function definition',
}
MSG_EXPLANATION = [
    r"""
    - A macro element can only be defined inside a define element.
      It must have `=` or `:=` and in case of a function it must
      start with `\\` and contain parameters inside `{...}`.

    - When using parameters they must be within `:`, that is, if
      `exp` is a paramter then you may use `:exp:` to refer to it
      inside the function definition.

    Okay:
        %%{define}
        x = 100
        \\SET{exp} := \left\{:exp:\right\}
        %%

    E100:
        %%{define}
        x 100
        \\SET{exp} := \left\{:exp:\right\}
        %%
    E101:
        %%{define}
        x = 100
        \\SET := \left\{:exp:\right\}
        %%
""",
]
