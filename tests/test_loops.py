from .test_interpreter import stmt_test_template
from .test_circuits import circuit_test_template
import circuits.gates as gates

# def circuit_test_template(code: str, gates_expected: List[Tuple[type, List[int]]]):

def test_simple_for_loop():
    stmt_test_template("""
    for i in 0..3 {
      print(i);
    }
    """,
    ['0', '1', '2'])

def test_squares_loop():
    stmt_test_template("""
    for i in 0..4 {
      print(i * i);
    }
    """,
    ['0', '1', '4', '9'])

def test_simple_qubit_loop():
    circuit_test_template("""
    q <- ?false;
    for i in 0..3 {
      q <- ~q;
    }
    """,
    [(gates.NotGate, [0])] * 3)

def test_two_qubit_loop():
    """This test should pass *only* any circuit optimizations enabled.
    """
    circuit_test_template("""
    q <- ?false;
    r <- ?false;
    for stage in 0..4 {
      q <- ~q;
      if q {
        r <- ~r;
      }
    }
    """,
    [(gates.NotGate, [0]), (gates.CnotGate, [0, 1])] * 4)
