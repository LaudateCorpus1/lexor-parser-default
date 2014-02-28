"""LEXOR: DEFAULT parser COMMENT test

Testing suite to parse lexor comment in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_comment():
    """lexor.parser.default.comment: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'comment'
    )
