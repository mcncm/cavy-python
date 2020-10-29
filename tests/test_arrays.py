from environment import MovedValueError
from .templates import circuit_test_template, stmt_test_template

import circuits.gates as gates

def test_numeric_array_clone():
    stmt_test_template("""
    arr <- [1, 2, 3];
    x <- arr;
    y <- arr;
    print x[0]; print x[1]; print x[2];
    print y[0]; print y[1]; print y[2];
    """,
    ['1', '2', '3'] * 2)

def test_qubit_array_no_cloning():
    circuit_test_template("""
        reg <- [?false; 3];
        r <- reg;
        s <- reg;
        """,
        [],
        exception=MovedValueError
    )

def test_qubit_array_rebinding():
    circuit_test_template("""
        reg <- [?false; 2];
        for q in reg {
            q <- split(q);
        }
        s <- reg[0];
        s <- ~s;
        """,
        [(gates.HadamardGate, [0]),
         (gates.HadamardGate, [1]),
         (gates.NotGate, [0])]
    )

def test_qubit_array_extensional():
    circuit_test_template(
        "reg <- [split(?false), ?true];",
        [(gates.HadamardGate, [0]), (gates.NotGate, [1])]
    )

def test_qubit_array_conditional():
    circuit_test_template("""
        reg <- [split(?false); 3];
        q <- ?false;
        if reg[1] {
            q <- ~q;
        }
        """,
        [(gates.HadamardGate, [0]),
         (gates.HadamardGate, [1]),
         (gates.HadamardGate, [2]),
         (gates.CnotGate, [1, 3])],
    )
