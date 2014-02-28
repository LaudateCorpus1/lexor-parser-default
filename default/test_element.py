"""LEXOR: DEFAULT parser ELEMENT test

Testing suite to parse lexor element in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_element():
    """lexor.parser.default.element: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'element'
    )
