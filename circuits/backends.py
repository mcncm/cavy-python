"""Hardware and simulation backends for Pycavy circuits"""
from abc import ABC, abstractmethod
from typing import Any, Dict

import dependencies as deps


class Backend(ABC):

    @abstractmethod
    def sample_circuit(self, circuit, reps: int) -> Dict[str, Any]:
        pass


class CirqBackend(Backend):
    """Use Cirq to simulate the circuit's output
    """

    @deps.require('cirq')
    def __init__(self):
        pass

    def sample_circuit(self, circuit, reps: int) -> Dict[str, Any]:
        samples = deps.cirq.sample(circuit.to_cirq(),
                                   dtype=bool,
                                   repetitions=reps)
        results = samples.measurements
        return {label: results.get(str((index, 0))).transpose()[0]
                for (label, index) in circuit.qubit_labels.items()}
