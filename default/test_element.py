"""LEXOR: DEFAULT parser ELEMENT test

Testing suite to parse lexor element in the default style.

"""
from nose.tools import eq_
from lexor.command.test import nose_msg_explanations
from lexor.core.parser import Parser

PARSER = Parser('lexor', 'default')


def test_element():
    """lexor.parser.default.element: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'element'
    )


def test_e100():
    """lexor.parser.default.element: E100 """
    PARSER.parse('<apple att1="a < b"></apple>\n')
    log = PARSER.log
    eq_(len(log), 2)
    eq_(log[0]['code'], 'E100')
    eq_(log[0]['module'], 'lexor-lang_lexor_parser_default_element')
    eq_(log[1]['code'], 'E100')
    eq_(log[1]['module'], 'lexor-lang_lexor_parser_default_entity')
