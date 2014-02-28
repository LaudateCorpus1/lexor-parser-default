"""LEXOR: DEFAULT parser HEADER test

Testing suite to parse lexor header in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_header():
    """lexor.parser.default.header: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'header'
    )
