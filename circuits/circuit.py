from typing import Set

import dependencies as deps
from .gates import Gate


class Circuit:
    def __init__(self):
        self.gates = []

    def add_gate(self, gate: Gate):
        self.gates.append(gate)

    def all_qubits(self) -> Set[int]:
        """All the qubits used in any gate"""
        qubits = []
        for gate in self.gates:
            qubits += gate.qubits
        return set(qubits)

    @deps.require('cirq')
    def to_cirq(self):
        qubits = [deps.cirq.GridQubit(i, 0) for i in self.all_qubits()]
        cirq_gates = [gate.to_cirq(qubits) for gate in self.gates]
        return deps.cirq.Circuit(*cirq_gates)
