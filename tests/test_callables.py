from contextlib import redirect_stdout
from io import StringIO

from interpreter import Interpreter
from lexer import Lexer
from lang_parser import Parser


def code_trace(code):
    statements = Parser(Lexer(code).lex()).parse()
    output = StringIO()
    with redirect_stdout(output):
        Interpreter().interpret(statements)
    output_lines = output.getvalue().split('\n')
    return list(filter(lambda s: len(s) > 0, output_lines))


def test_simple_callable():
    trace = code_trace("""
    x <- 27;
    debug(x);
    """)
    assert len(trace) == 1
    assert '27' in trace[0]
