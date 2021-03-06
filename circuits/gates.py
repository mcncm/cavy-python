from abc import ABC, abstractmethod
from copy import copy
from typing import List

import dependencies as deps


class Gate:
    arity = -1

    def __init__(self, *qubits: List[int], conj=False):
        assert len(qubits) == self.arity
        self.qubits = qubits  # The qubits on which this gate acts
        self.conj = conj      # True if this gate is conjugated

    @abstractmethod
    def with_control(self, control: int) -> List['Gate']:
        return [Gate([])]

    def conjugate(self) -> 'Gate':
        new_gate = copy(self)
        new_gate.conj = not self.conj
        return new_gate


class StrongMeasurementGate(Gate):
    """A strong measurement; that is, the "ordinary" sort usually seen in circuit
    diagrams.
    """

    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.measure(qubits[self.qubits[0]])

    def with_control(self, control: int) -> List[Gate]:
        # TODO I'm not *quite* sure what to do here, to tell the truth.
        raise NotImplementedError

    def conjugate(self) -> Gate:
        raise NotImplementedError


class NotGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.X(qubits[self.qubits[0]])

    def with_control(self, control: int) -> List[Gate]:
        return [CnotGate(control, self.qubits[0])]

    def conjugate(self) -> Gate:
        return self


class ZGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.Z(qubits[self.qubits[0]])

    def with_control(self, control: int) -> List[Gate]:
        return [
            HadamardGate(self.qubits[0]),
            CnotGate(control, self.qubits[0]),
            HadamardGate(self.qubits[0])
        ]

class TGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        if self.conj:
            cirq_gate = deps.cirq.inverse(deps.cirq.T)
        else:
            cirq_gate = deps.cirq.T
        return cirq_gate(qubits[self.qubits[0]])

    def with_control(self, control: int) -> List[Gate]:
        raise NotImplementedError
        return []


class HadamardGate(Gate):
    arity = 1

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.H(qubits[self.qubits[0]])

    def with_control(self, control: int) -> List[Gate]:
        raise NotImplementedError
        return []


class CnotGate(Gate):
    """A controlled-NOT gate acting on two qubits. qubit 0 is the controller; qubit
    1 the controllee.
    """
    arity = 2

    @deps.require('cirq')
    def to_cirq(self, qubits):
        return deps.cirq.CNOT(qubits[self.qubits[0]], qubits[self.qubits[1]])

    def with_control(self, control: int) -> List[Gate]:
        return [
            HadamardGate(self.qubits[1]),
            CnotGate(self.qubits[0], self.qubits[1]),
            TGate(self.qubits[1], conj=True),
            CnotGate(control, self.qubits[1]),
            TGate(self.qubits[1]),
            CnotGate(self.qubits[0], self.qubits[1]),
            TGate(self.qubits[1], conj=True),
            CnotGate(control, self.qubits[1]),
            TGate(self.qubits[0]),
            TGate(self.qubits[1]),
            CnotGate(control, self.qubits[0]),
            HadamardGate(self.qubits[1]),
            TGate(control),
            TGate(self.qubits[0], conj=True),
            CnotGate(control, self.qubits[0]),
        ]
