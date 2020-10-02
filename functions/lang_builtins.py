from .function import AbstractFunction
from circuits.circuit import Circuit
import circuits.gates as gates
from lang_types import Qubit


class AllocQubit(AbstractFunction):
    """Allocates and returns a single qubit"""
    arity = 0

    def call(self, interp, args) -> Qubit:
        return interp.environment.alloc_one()


class Split(AbstractFunction):
    """Implements a logical Hadamard operation on a single qubit"""
    arity = 1

    def call(self, interp, args) -> Qubit:
        qubit = args[0]
        gates_ = interp.environment.embed_gate(gates.HadamardGate(qubit.index))
        interp.circuit.add_gates(gates_)
        return qubit


class Phase(AbstractFunction):
    """Implements a logical phase gate on a single qubit"""
    arity = 1

    def call(self, interp, args) -> Qubit:
        qubit = args[0]
        gates_ = interp.environment.embed_gate(gates.PhaseGate(qubit.index))
        interp.circuit.add_gates(gates_)
        return qubit


class Debug(AbstractFunction):
    """A debug function that prints a debug message"""
    arity = 1

    def call(self, interp, args) -> None:
        print(f"Called `debug` with flag {args[0]}")
