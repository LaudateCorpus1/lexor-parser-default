"""LEXOR: LIST NodeParser

Parses list enviroments. To add attributes to the list
you may use square brackets and curly braces to add attributes
to the item list. For instance

    %%{list}
    +[#ol_id]{#first_item} Item 1
    +{#second_item} Item 2
    %%

Will be parsed to:

    list:
        list_item[level="1" type="ol" __id="ol_id" _id="first_item"]:
            p[remove="true"]:
                #text: 'Item 1'
        list_item[level="1" type="ol" _id="second_item"]:
            p[remove="true"]:
                #text: 'Item 2'

"""

from lexor.core.parser import NodeParser
from lexor.core.elements import Element


class ListNP(NodeParser):
    """Look for list elements. """

    def make_node(self):
        parser = self.parser
        index = parser.caret + 1
        char = parser.text[index]
        if parser.text[index-1] != '\n' or char not in '*+^':
            return None
        if char == '^':
            index += 1
            char = parser.text[index]
            if char not in '*+':
                return None
            flag = 'close'
            total = 0
            while parser.text[index] == char:
                index += 1
                total += 1
        else:
            flag = None
            total = 0
            while parser.text[index] == char:
                index += 1
                total += 1
        node = Element('list_item')
        if flag is not None:
            node['flag'] = flag
        node['level'] = total
        if char == '*':
            node['type'] = 'ul'
        else:
            node['type'] = 'ol'
        node.pos = parser.copy_pos()
        parser.update(index)
        total = node.attlen
        parser['ElementNP'].get_attribute_list(parser, node, '[', ']')
        for num in xrange(total, node.attlen):
            node.rename(num, '__'+node.attribute(num))
        total = node.attlen
        parser['ElementNP'].get_attribute_list(parser, node)
        for num in xrange(total, node.attlen):
            node.rename(num, '_'+node.attribute(num))
        if parser.text[parser.caret] == ' ':
            parser.update(parser.caret+1)
        return node

    def close(self, _):
        parser = self.parser
        caret = parser.caret
        if parser.text[caret:caret+3] == '\n%%':
            pos = parser.copy_pos()
            parser.update(caret+1)
            return pos
        if parser.text[caret] == '\n' and parser.text[caret+1] in '*+^':
            return parser.copy_pos()
