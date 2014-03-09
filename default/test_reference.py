"""LEXOR: DEFAULT parser REFERENCE test

Testing suite to parse lexor reference in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_reference():
    """lexor.parser.default.reference: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'reference'
    )
