"""LEXOR: DEFAULT parser EVAL test

Testing suite to parse lexor eval in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_eval():
    """lexor.parser.default.eval: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'eval'
    )
