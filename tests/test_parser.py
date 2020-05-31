from typing import Tuple, Callable

from lexer import Lexer
from lang_parser import Parser, Expression, s_expr


def expr_test_template(code, tree: Tuple):
    """Generates a test case comparing the AST produced by the parser with a
    hand-written S-expression.
    """
    ast = Parser(Lexer(code).lex()).expression()
    assert s_expr(ast) == tree


def test_simple_equality():
    expr_test_template(
        '123 == 4567',
        ('EQUALEQUAL', 123, 4567)
    )


def test_group():
    expr_test_template(
        '1 + ((2 + 3) + 4)',
        ('PLUS', 1, ('PLUS', ('PLUS', 2, 3), 4))
    )


def test_star_1():
    expr_test_template(
        '1 * 2 + 3',
        ('PLUS', ('STAR', 1, 2), 3)
    )

def test_star_2():
    expr_test_template(
        '3 + 1 * 2',
        ('PLUS', 3, ('STAR', 1, 2))
    )


# Not yet passing! No support yet for identifiers.
#
# def test_idents():
#     ast_test_template('foo == bar * 3', (
#         'EQUALEQUAL', 'foo', ('STAR', 'bar', 3)
#     ))
