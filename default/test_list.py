"""LEXOR: DEFAULT parser LIST test

Testing suite to parse lexor list in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_list():
    """lexor.parser.default.list: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'list'
    )
