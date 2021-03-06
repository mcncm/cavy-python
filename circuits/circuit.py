from typing import Set, List, Optional, Dict, Any

import dependencies as deps
from .gates import Gate
from lang_types import Qubit

class Circuit:
    def __init__(self):
        self.gates = []
        self.qubit_labels = {}

    # def add_gate(self, gate: Gate, control: Optional[Qubit] = None):
    #     if control:
    #         self.gates.append(gate.with_control(control))
    #     else:
    #         self.gates.append(gate)

    def add_gates(self, gates: List[Gate]):
        self.gates += gates

    def all_qubits(self) -> Set[int]:
        """All the qubits used in any gate"""
        qubits = []
        for gate in self.gates:
            qubits += gate.qubits
        return set(qubits)

    def to_backend(self, backend: Optional[str]):
       if backend == None:
           return self
       elif backend == 'cirq':
           return self.to_cirq()
       elif backend == 'diagram':
           return self.to_diagram()
       else:
           # TODO fix error handling here
           # Probably make a `Backend` class and move error handling
           # into its `__init__` method
           raise ValueError('Invalid backend: {}', backend)

    def sample(self, backend, reps: int = 1) -> Dict[str, Any]:
        """Sample the circuit on all-zero input using a given backend"""
        assert reps >= 1
        return backend.sample_circuit(self, reps)

    @deps.require('cirq')
    def to_cirq(self):
        qubits = [deps.cirq.GridQubit(i, 0) for i in self.all_qubits()]
        cirq_gates = [gate.to_cirq(qubits) for gate in self.gates]
        return deps.cirq.Circuit(*cirq_gates)

    def to_qasm(self):
        """Transform this circuit to a QASM string representation. For the time being,
        we'll rely on Cirq as an intermediate representation. In a future
        version, I'd ideally prefer not to.

        """
        circuit = self.to_cirq()
        return deps.cirq.qasm(circuit)

    @deps.require('__unsatisfiable__')
    def __to_qasm_native(self):
        """Transform this circuit to a QASM string representation
        TODO implement this!
        """
        raise NotImplementedError

    @deps.require('labber')
    def to_labber(self):
        """Transform this circuit to a Labber circuit that can be run
        on a physical machine.
        TODO implement this!
        """
        raise NotImplementedError

    @deps.require('cirq', 'pylatex')
    def to_diagram(self) -> str:
        """Returns latex source for a circuit diagram
        """
        to_latex = deps.cirq.contrib.qcircuit.circuit_to_latex_using_qcircuit
        circuit = self.to_cirq()
        return to_latex(circuit, circuit.all_qubits())
