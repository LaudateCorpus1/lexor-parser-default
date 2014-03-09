"""LEXOR: DEFAULT parser DEFINE test

Testing suite to parse lexor define in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_define():
    """lexor.parser.default.define: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'define'
    )
