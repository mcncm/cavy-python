from contextlib import redirect_stdout
from io import StringIO
from typing import List, Tuple

from lexer import Lexer
from interpreter import Interpreter
from lang_parser import Parser
import circuits.gates as gates

import cirq
import numpy as np


def unitary_test_template(code: str, unitary_expected: np.array):
    """Checks that the circuit produced by a code snippet matches a template
    numerically. The template is given as a unitary matrix."""
    interpreter = Interpreter()
    statements = Parser(Lexer(code).lex()).parse()
    interpreter.interpret(statements)
    circuit = interpreter.circuit.to_cirq()
    unitary = cirq.unitary(circuit)
    assert np.allclose(unitary, unitary_expected)


def test_not():
    unitary_test_template("q <- ~qubit();", np.array([[0, 1], [1, 0]]))


def test_z_gate():
    unitary_test_template("q <- flip(qubit());", np.array([[1, 0], [0, -1]]))


def test_hadamard():
    unitary_test_template("q <- split(qubit());",
                          np.array([[1, 1], [1, -1]] / np.sqrt(2)))


def cnot_test_template(n: int):
    """Tests a ccc...cnot circuit, nested n times. e.g. for n = 2,
    this produces the Cavy code

      q <- qubit();
      r <- qubit();
      s <- qubit();
      if q {
        if r {
          s <- ~s;
        }
      }

    """
    declarations = '\n'.join([f"q{i} <- qubit();" for i in range(n)])
    declarations += "r <- qubit();"
    if_stmt = ' '.join([f"if q{i} {{" for i in range(n)]) + "r <- ~r;" + n * "}"

    unitary_expected = np.eye(2 ** (n + 1))
    unitary_expected[-2:, -2:] = np.array([[0, 1], [1, 0]])

    unitary_test_template(declarations + if_stmt, unitary_expected)


def test_cnot():
    cnot_test_template(1)

def test_ccnot():
    cnot_test_template(2)
