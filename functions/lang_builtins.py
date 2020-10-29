from .function import AbstractFunction
import circuits.gates as gates
from lang_types import Array, Qubit

from typing import Union


class AllocQubit(AbstractFunction):
    """Allocates and returns a single qubit"""
    arity = 0

    def call(self, interp, args) -> Qubit:
        return interp.environment.alloc_one()


class VectorizedGate(AbstractFunction):
    """A 'polymorphic' function that applies gates to single qubits, or mapped over
    arrays of qubits. Subclases should provide a `_call` method that implements
    the operation on a single qubit.
    """
    arity = 1

    def call(self, interp, args) -> Union[Array, Qubit]:
        arg = args[0]
        if isinstance(arg, Qubit):
            return self._call(interp, [arg])
        elif isinstance(arg, Array):
            newarr = Array([self.call(interp, [elem]) for elem in arg])
            return newarr
        else:
            raise NotImplementedError

class Split(VectorizedGate):
    """Implements a logical Hadamard operation on a single qubit"""
    arity = 1

    def _call(self, interp, args) -> Qubit:
        qubit = args[0]
        gates_ = interp.environment.embed_gate(gates.HadamardGate(qubit.index))
        interp.circuit.add_gates(gates_)
        return qubit


class Flip(VectorizedGate):
    """Implements a logical Z gate on a single qubit"""
    arity = 1

    def _call(self, interp, args) -> Qubit:
        qubit = args[0]
        gates_ = interp.environment.embed_gate(gates.ZGate(qubit.index))
        interp.circuit.add_gates(gates_)
        return qubit


class Debug(AbstractFunction):
    """A debug function that prints a debug message"""
    arity = 1

    def call(self, interp, args) -> None:
        print(f"Called `debug` with flag {args[0]}")
