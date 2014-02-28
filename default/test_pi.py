"""LEXOR: DEFAULT parser PI test

Testing suite to parse lexor pi in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_pi():
    """lexor.parser.default.pi: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'pi'
    )
