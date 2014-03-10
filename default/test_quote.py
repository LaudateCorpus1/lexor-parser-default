"""LEXOR: DEFAULT parser QUOTE test

Testing suite to parse lexor quote in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_quote():
    """lexor.parser.default.quote: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'quote'
    )
