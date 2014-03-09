"""LEXOR: DEFAULT parser LATEX test

Testing suite to parse lexor latex in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_latex():
    """lexor.parser.default.latex: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'latex'
    )
