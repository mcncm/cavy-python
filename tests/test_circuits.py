from contextlib import redirect_stdout
from io import StringIO
from typing import List, Tuple

from environment import MovedValueError
from lexer import Lexer
from interpreter import Interpreter
from lang_parser import Parser
import circuits.gates as gates

import pytest

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


def test_no_qubits():
    circuit_test_template("v <- 1; print v;", [])


def test_one_qubit():
    circuit_test_template(
        "q <- qubit();",
        []
    )


def test_one_move():
    circuit_test_template(
        "q <- qubit(); r <- q;",
        []
    )

def test_no_cloning():
    circuit_test_template(
        "q <- qubit(); r <- q; s <- q;",
        [],
        exception=MovedValueError
    )

def test_two_qubits():
    circuit_test_template(
        "q1 <- qubit(); q2 <- qubit();",
        []
    )


def test_one_false():
    """Test the (dubious) ? syntax for linearization"""
    circuit_test_template(
        "q <- ?false;",
        []
    )

def test_one_true():
    """Test the (dubious) ? syntax for linearization"""
    circuit_test_template(
        "q <- ?true;",
        [(gates.NotGate, [0])]
    )
def test_one_split():
    circuit_test_template(
        "q <- split(qubit());",
        [(gates.HadamardGate, [0])]
    )


def test_two_split():
    circuit_test_template(
        "q1 <- split(qubit()); q2 <- split(qubit());",
        [(gates.HadamardGate, [0]), (gates.HadamardGate, [1])]
    )


def test_not_gate():
    circuit_test_template(
        "q <- ~qubit();",
        [(gates.NotGate, [0])]
    )


def test_z_gate():
    circuit_test_template(
        "q <- split(qubit()); r <- flip(q);",
        [(gates.HadamardGate, [0]), (gates.ZGate, [0])]
    )

def test_cnot_gate():
    circuit_test_template("""
        q <- ?false;
        r <- ?false;
        if q {
            r <- ~r;
        }
        """,
        [(gates.CnotGate, [0, 1])]
    )

def test_contravariant_eval_not():
    circuit_test_template("""
        q <- ?false;
        r <- ?false;
        if ~q {
            r <- ~r;
        }
        """,
        [(gates.NotGate, [0]),
         (gates.CnotGate, [0, 1]),
         (gates.NotGate, [0])]
    )

def test_contravariant_eval_z():
    circuit_test_template("""
        q <- ?false;
        r <- ?false;
        if flip(q) {
            r <- ~r;
        }
        """,
        [(gates.ZGate, [0]),
         (gates.CnotGate, [0, 1]),
         (gates.ZGate, [0])]
    )

def test_contravariant_eval_split_not():
    circuit_test_template("""
        q <- ?false;
        r <- ?false;
        if split(~q) {
            r <- ~r;
        }
        """,
        [(gates.HadamardGate, [0]),
         (gates.NotGate, [0]),
         (gates.CnotGate, [0, 1]),
         (gates.NotGate, [0]),
         (gates.HadamardGate, [0])]
    )
