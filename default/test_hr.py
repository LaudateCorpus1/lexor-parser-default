"""LEXOR: DEFAULT parser HR test

Testing suite to parse lexor hr in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_hr():
    """lexor.parser.default.hr: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'hr'
    )
