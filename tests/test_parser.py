from typing import Tuple, Callable

from lexer import Lexer
from lang_parser import Parser, Expression, s_expr

def code_to_s_expr(code):
    return s_expr(Parser(Lexer(code).lex()).expression())

def expr_test_template(code, tree: Tuple):
    """Generates a test case comparing the AST produced by the parser with a
    hand-written S-expression.

    TODO: there's another `expr_test_template` function in templates.py that
    does something slightly different. Combine these if you can.
    """
    assert code_to_s_expr(code) == tree


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

def test_star_left_assoc_1():
    expr_test_template(
        '2 * 3 * 4',
        ('STAR', ('STAR', 2, 3), 4)
    )

def test_star_left_assoc_2():
    expr_test_template(
        '2 * (3 * 4)',
        ('STAR', 2, ('STAR', 3, 4))
    )

def test_caret_right_assoc_1():
    expr_test_template(
        '2 ^ 3 ^ 4',
        ('CARET', 2, ('CARET', 3, 4))
    )

def test_caret_right_assoc_2():
    expr_test_template(
        '(2 ^ 3) ^ 4',
        ('CARET', ('CARET', 2, 3), 4)
    )

def test_big_simple():
    expr_test_template(
                       '  1 +   2 *  3 ^   (4 + 5  == 6) ^ 7    * 8   + 9  == 3',
        code_to_s_expr('((1 + ((2 * (3 ^ (((4 + 5) == 6) ^ 7))) * 8)) + 9) == 3')
    )

# Not yet passing! No support yet for identifiers.
#
# def test_idents():
#     ast_test_template('foo == bar * 3', (
#         'EQUALEQUAL', 'foo', ('STAR', 'bar', 3)
#     ))
