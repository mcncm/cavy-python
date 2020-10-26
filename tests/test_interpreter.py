from lexer import Lexer
from interpreter import Interpreter
from lang_parser import Parser

from contextlib import redirect_stdout
from io import StringIO

import pytest

def expr_test_template(code, value_expected):
    """Generates a test case comparing the AST produced by the parser with a
    hand-written S-expression.
    """
    ast = Parser(Lexer(code).lex()).expression()
    assert Interpreter().evaluate(ast) == value_expected


def test_simple_addition():
    expr_test_template("1 + 1", 2)


def test_assoc_1():
    expr_test_template("(2 * 4) + 3", 11)


def test_assoc_2():
    expr_test_template("2 * (4 + 3)", 14)


def test_eq_1():
    expr_test_template("7 + 2 == 3 * 3", True)


def test_eq_2():
    expr_test_template("0 == 1", False)


def test_neq():
    expr_test_template("true ~= false", True)


def stmt_test_template(code, trace_expected, exception=None):
    """
    Here 'exception' is either None, or an expected exception type.
    """
    statements = Parser(Lexer(code).lex()).parse()
    output = StringIO()
    with redirect_stdout(output):
        if exception is None:
            Interpreter().interpret(statements)
        else:
            with pytest.raises(exception):
                Interpreter().interpret(statements)
    trace_actual = output.getvalue().split()
    assert trace_actual == trace_expected


def test_simple_print():
    stmt_test_template("print 0;", ['0'])


def test_multiple_print():
    stmt_test_template("print 12; print true;", ['12', 'True'])


def test_complex_statements():
    stmt_test_template('print 4 * 3; print true ~= true; print 7 + 24;',
                       ['12', 'False', '31'])

def test_silent_statement():
    stmt_test_template('print 8; 12 + 6; print false;', ['8', 'False'])

def test_simple_assignment():
    stmt_test_template('v <- 1; print v;', ['1'])

def test_reassignment_1():
    stmt_test_template('v <- 1; v <- 2; print v;', ['2'])

def test_reassignment_2():
    stmt_test_template('v <- 1; v <- v + 1; print v;', ['2'])

def test_variable_arithmetic():
    stmt_test_template('x <- 3; y <- 4; print 3 * 4;', ['12'])

def test_simple_function_definition():
    stmt_test_template("""
        fn printTwice(x) {
            print(x);
            print(x);
        }

        printTwice(4);
    """, ['4', '4'])
