"""LEXOR: AUTO NodeParser

Contains the AutoMail and AutoLink node parsers.

"""

import re
from lexor.core.parser import NodeParser
from lexor.core.elements import Element, Text

MAIL_RE = re.compile(r'([^> \!]*@[^> ]*)')
URL_RE = re.compile(r'((?:[Ff]|[Hh][Tt])[Tt][Pp][Ss]?://[^>]*)')


class AutoMailNP(NodeParser):
    """Parse email address enclosed by `<` and `>`. """

    @staticmethod
    def is_auto_mail(parser, begin, end):
        """Check if the parser is at <user@domain>"""
        if parser.text[begin] != '<':
            return None
        index = parser.text.find('>', begin, end)
        if index == -1:
            return None
        match = MAIL_RE.match(parser.text[begin+1:index])
        if not match:
            return None
        return index

    def make_node(self):
        parser = self.parser
        index = self.is_auto_mail(parser, parser.caret, parser.end)
        if index is None:
            return None
        email = parser.text[parser.caret+1:index]
        mailto = "mailto:" + email
        node = Element('a')
        node['href'] = mailto
        node.append_child(Text(email))
        parser.update(index+1)
        parser['ElementNP'].get_attribute_list(parser, node)
        return [node]


class AutoLinkNP(NodeParser):
    """Parse urls enclosed by `<` and `>`. """

    @staticmethod
    def is_auto_link(parser, begin, end):
        """Check if the parser is at <url>"""
        if parser.text[begin] != '<':
            return None
        index = parser.text.find('>', begin, end)
        if index == -1:
            return None
        match = URL_RE.match(parser.text[begin+1:index])
        if not match:
            return None
        return index

    def make_node(self):
        parser = self.parser
        index = self.is_auto_link(parser, parser.caret, parser.end)
        if index is None:
            return None
        url = parser.text[parser.caret+1:index]
        node = Element('a')
        node['href'] = url
        node.append_child(Text(url))
        parser.update(index+1)
        parser['ElementNP'].get_attribute_list(parser, node)
        return [node]
