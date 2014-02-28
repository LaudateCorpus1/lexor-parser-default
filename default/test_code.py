"""LEXOR: DEFAULT parser CODE test

Testing suite to parse lexor code in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_code():
    """lexor.parser.default.code: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'code'
    )
