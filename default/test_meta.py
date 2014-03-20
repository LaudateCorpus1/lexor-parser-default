"""LEXOR: DEFAULT parser META test

Testing suite to parse lexor meta in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_meta():
    """lexor.parser.default.meta: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'meta'
    )
