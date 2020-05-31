from lexer import Lexer
from interpreter import Interpreter
from lang_parser import Parser


def interp_test_template(code, value):
    """Generates a test case comparing the AST produced by the parser with a
    hand-written S-expression.
    """
    ast = Parser(Lexer(code).lex()).parse()
    assert Interpreter().evaluate(ast) == value


def test_simple_addition():
    interp_test_template("1 + 1", 2)

def test_assoc_1():
    interp_test_template("(2 * 4) + 3", 11)

def test_assoc_2():
    interp_test_template("2 * (4 + 3)", 14)

def test_eq_1():
    interp_test_template("7 + 2 == 3 * 3", True)

def test_eq_2():
    interp_test_template("0 == 1", False)

def test_neq():
    interp_test_template("true ~= false", True)
