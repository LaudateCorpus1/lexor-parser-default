"""LEXOR: DEFAULT parser INLINE test

Testing suite to parse lexor inline in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_inline():
    """lexor.parser.default.inline: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'inline'
    )
