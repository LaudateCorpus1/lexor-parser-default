"""LEXOR: DEFAULT parser AUTO test

Testing suite to parse lexor auto in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_auto():
    """lexor.parser.default.auto: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'auto'
    )
