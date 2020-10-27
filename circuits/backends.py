"""Hardware and simulation backends for Pycavy circuits"""
from abc import ABC, abstractmethod
from typing import Any, Dict

import dependencies as deps
from circuits.sample import Sample


class Backend(ABC):

    @abstractmethod
    def sample_circuit(self, circuit, reps: int) -> Sample:
        pass


class CirqBackend(Backend):
    """Use Cirq to simulate the circuit's output
    """

    @deps.require('cirq')
    def __init__(self):
        pass

    def sample_circuit(self, circuit, reps: int) -> Sample:
        def meas_index(measurements, i: int):
            return measurements.get(str((i, 0))).transpose()[0]
        results = deps.cirq.sample(circuit.to_cirq(),
                                   dtype=bool,
                                   repetitions=reps)
        samples = {label: meas_index(results.measurements, index)
                    for (label, index) in circuit.qubit_labels.items()}

        return Sample(samples)
