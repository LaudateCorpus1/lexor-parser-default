"""LEXOR: DEFAULT parser EMPTY test

Testing suite to parse lexor empty in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_empty():
    """lexor.parser.default.empty: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'empty'
    )
