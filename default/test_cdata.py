"""LEXOR: DEFAULT parser CDATA test

Testing suite to parse lexor cdata in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_cdata():
    """lexor.parser.default.cdata: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'cdata'
    )
