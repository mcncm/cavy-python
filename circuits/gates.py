from typing import List

import dependencies as deps


class Gate:
    arity = -1

    def __init__(self, *qubits: List[int]):
        assert len(qubits) == self.arity
        self.qubits = qubits


class NotGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.X(qubits[self.qubits[0]])


class PhaseGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.Z(qubits[self.qubits[0]])


class HadamardGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.H(qubits[self.qubits[0]])
