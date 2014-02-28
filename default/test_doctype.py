"""LEXOR: DEFAULT parser DOCTYPE test

Testing suite to parse lexor doctype in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_doctype():
    """lexor.parser.default.doctype: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'doctype'
    )
