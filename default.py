"""LEXOR: DEFAULT Parsing Style

This parser attempts to combine the best features of Markdown and
LaTeX. This is all in taste and preferences of the author.

"""

from lexor import init, load_aux

INFO = init(
    version=(0, 0, 1, 'rc', 2),
    lang='lexor',
    type='parser',
    description='Parse Markdown and LaTeX elements. ',
    url='http://jmlopez-rod.github.io/lexor-lang/lexor-parser-default',
    author='Manuel Lopez',
    author_email='jmlopez.rod@gmail.com',
    license='BSD License',
    path=__file__
)
MOD = load_aux(INFO)
REPOSITORY = [
    MOD['auto'].AutoLinkNP,
    MOD['auto'].AutoMailNP,
    MOD['cdata'].CDataNP,
    MOD['comment'].CommentNP,
    MOD['code'].CodeInlineNP,
    MOD['doctype'].DocumentTypeNP,
    MOD['element'].ElementNP,
    MOD['empty'].EmptyNP,
    MOD['entity'].EntityNP,
    MOD['entity'].BreakNP,
    MOD['header'].AtxHeaderNP,
    MOD['header'].SetextHeaderNP,
    MOD['inline'].StrongEmNP,
    MOD['inline'].EmStrongNP,
    MOD['inline'].StrongNP,
    MOD['inline'].Strong2NP,
    MOD['inline'].EmNP,
    MOD['inline'].SmartEmNP,
    MOD['latex'].LatexDisplayNP,
    MOD['latex'].LatexInlineNP,
    MOD['list'].ListNP,
    MOD['paragraph'].ParagraphNP,
    MOD['pi'].ProcessingInstructionNP,
    MOD['reference'].ReferenceBlockNP,
    MOD['reference'].ReferenceInlineNP,
]
MAPPING = {
    '__default__': (
        '<&\\\\`\'\"*_{}[\\]()#+-.!%$\n', [
            'CodeInlineNP',
            'ReferenceInlineNP',
            'LatexDisplayNP',
            'LatexInlineNP',
            'StrongEmNP',
            'EmStrongNP',
            'StrongNP',
            'Strong2NP',
            'EmNP',
            'SmartEmNP',
            'BreakNP',
            'AutoMailNP',
            'AutoLinkNP',
            'ElementNP',
            'CDataNP',
            'DocumentTypeNP',
            'CommentNP',
            'ProcessingInstructionNP',
            'EntityNP',
        ]
    ),
    '#document': (
        '\n', [
            'EmptyNP',
            'ReferenceBlockNP',
            #CodeBlockNP,
            'AtxHeaderNP',
            'SetextHeaderNP',
            'LatexDisplayNP',
            'BreakNP',
            'CDataNP',
            'DocumentTypeNP',
            'CommentNP',
            'ProcessingInstructionNP',
            'ParagraphNP',
            'ElementNP',
        ]
    ),
    'body': '#document',
    'list': (
        '\n', [
            'ListNP',
        ]
    ),
    'list_item': '#document',
    'align': ('%', []),
    'equation': ('%', []),
    'define': (
        '\n', [
            MOD['define'].MacroNP,
        ]
    ),
}
