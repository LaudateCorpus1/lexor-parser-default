"""LEXOR: DEFAULT parser PARAGRAPH test

Testing suite to parse lexor paragraph in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_paragraph():
    """lexor.parser.default.paragraph: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'paragraph'
    )
