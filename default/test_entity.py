"""LEXOR: DEFAULT parser ENTITY test

Testing suite to parse lexor entity in the default style.

"""

from lexor.command.test import nose_msg_explanations


def test_entity():
    """lexor.parser.default.entity: MSG_EXPLANATION """
    nose_msg_explanations(
        'lexor', 'parser', 'default', 'entity'
    )
