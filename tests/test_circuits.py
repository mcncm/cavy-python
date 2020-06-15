from contextlib import redirect_stdout
from io import StringIO
from typing import List, Tuple

from lexer import Lexer
from interpreter import Interpreter
from lang_parser import Parser
import circuits.gates as gates


def circuit_test_template(code: str, gates_expected: List[Tuple[type, List[int]]]):
    """Checks that the circuit produced by a code snippet matches a template
    exactly. The template is given"""
    interpreter = Interpreter()
    statements = Parser(Lexer(code).lex()).parse()
    interpreter.interpret(statements)
    gates = interpreter.environment.circuit.gates
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
        "q <- qubit(); r <- q",
        []
    )


def test_two_qubits():
    circuit_test_template(
        "q1 <- qubit(); q2 <- qubit()",
        []
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


def test_phase_gate():
    circuit_test_template(
        "q <- ~qubit();",
        [(gates.NotGate, [0])]
    )


def test_phase_gate():
    circuit_test_template(
        "q <- split(qubit()); r <- phase(q);",
        [(gates.HadamardGate, [0]), (gates.PhaseGate, [0])]
    )
