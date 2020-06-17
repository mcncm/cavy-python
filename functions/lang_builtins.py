from environment import Environment
from .function import Function
from circuits.circuit import Circuit
import circuits.gates as gates
from lang_types import Qubit


class AllocQubit(Function):
    """Allocates and returns a single qubit"""
    arity = 0

    def call(self, env: Environment, circuit: Circuit, args) -> Qubit:
        return env.alloc_one()


class Split(Function):
    """Implements a logical Hadamard operation on a single qubit"""
    arity = 1

    def call(self, env: Environment, circuit: Circuit, args) -> Qubit:
        qubit = args[0]
        gates_ = env.embed_gate(gates.HadamardGate(qubit.index))
        circuit.add_gates(gates_)
        return qubit


class Phase(Function):
    """Implements a logical phase gate on a single qubit"""
    arity = 1

    def call(self, env: Environment, circuit: Circuit, args) -> Qubit:
        qubit = args[0]
        gates_ = env.embed_gate(gates.PhaseGate(qubit.index))
        circuit.add_gates(gates_)
        return qubit


class Debug(Function):
    """A debug function that prints a debug message"""
    arity = 1

    def call(self, env: Environment, circuit: Circuit, args) -> None:
        print(f"Called `debug` with flag {args[0]}")
