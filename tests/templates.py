from contextlib import redirect_stdout
from io import StringIO
from typing import List, Tuple

from interpreter import Interpreter
from lang_parser import Parser
from lexer import Lexer

import pytest
import numpy as np
import cirq


def token_test_template(code, token_types):
    lexer = Lexer(code)
    tokens = lexer.lex()
    tokens.pop(-1)  # ignore eof
    lexed_token_types = list(map(lambda t: t.token_type, tokens))

    assert len(lexed_token_types) == len(token_types)

    for (lexed_tt, spec_tt) in zip(lexed_token_types, token_types):
        assert lexed_tt == spec_tt


def expr_test_template(code, value_expected):
    """Generates a test case comparing the AST produced by the parser with a
    hand-written S-expression.
    """
    ast = Parser(Lexer(code).lex()).expression()
    assert Interpreter().evaluate(ast) == value_expected


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


def unitary_test_template(code: str, unitary_expected: np.array):
    """Checks that the circuit produced by a code snippet matches a template
    numerically. The template is given as a unitary matrix."""
    interpreter = Interpreter()
    statements = Parser(Lexer(code).lex()).parse()
    interpreter.interpret(statements)
    circuit = interpreter.circuit.to_cirq()
    unitary = cirq.unitary(circuit)
    assert np.allclose(unitary, unitary_expected)


def circuit_test_template(code: str, gates_expected: List[Tuple[type, List[int]]],
                          exception=None):
    """Checks that the circuit produced by a code snippet matches a template
    exactly. The template is given"""
    interpreter = Interpreter()
    statements = Parser(Lexer(code).lex()).parse()
    if exception is None:
        interpreter.interpret(statements)
    else:
        with pytest.raises(exception):
            Interpreter().interpret(statements)
    gates = interpreter.circuit.gates
    assert len(gates) == len(gates_expected)
    for (gate, (type_expected, qubits_expected)) in zip(gates, gates_expected):
        assert type(gate) == type_expected
        assert list(gate.qubits) == qubits_expected
