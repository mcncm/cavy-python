from typing import Tuple, Callable

from lexer import Lexer
from langparser import Parser, Expression, s_expr


def ast_test_template(code, tree: Tuple):
    """Generates a test case comparing the AST produced by the parser with a
    hand-written S-expression.
    """
    ast = Parser(Lexer(code).lex()).parse()
    assert s_expr(ast) == tree

def test_simple_equality():
    ast_test_template('123 == 4567', (
        'EQUALEQUAL', 123, 4567
    ))

def test_group():
    ast_test_template('1 + ((2 + 3) + 4)', (
        'PLUS', 1, ('PLUS', ('PLUS', 2, 3), 4)
    ))

# Not yet passing! No support yet for identifiers.
#
# def test_idents():
#     ast_test_template('foo == bar * 3', (
#         'EQUALEQUAL', 'foo', ('STAR', 'bar', 3)
#     ))
