from environment import Environment
from .function import Function
import circuits.gates as gates
from lang_types import Qubit


class AllocQubit(Function):
    """Allocates and returns a single qubit"""
    arity = 0

    def call(self, env: Environment, args) -> Qubit:
        return env.alloc_one()


class Split(Function):
    """Implements a logical Hadamard operation on a single qubit"""
    arity = 1

    def call(self, env: Environment, args) -> Qubit:
        qubit = args[0]
        env.add_gate(gates.HadamardGate(qubit.index))
        return qubit


class Phase(Function):
    """Implements a logical phase gate on a single qubit"""
    arity = 2

    def call(self, env: Environment, args) -> Qubit:
        raise NotImplementedError


class Debug(Function):
    """A debug function that prints a debug message"""
    arity = 1

    def call(self, env: Environment, args) -> None:
        print(f"Called `debug` with flag {args[0]}")
