from enum import Enum, auto
from typing import Any


class TypingDiscipline(Enum):
    UNRESTRICTED = auto()
    LINEAR = auto()
    AFFINE = auto()
    NONCOMMUTATIVE = auto()


class CavyType:
    pass


class QubitState:
    LIVE = auto()
    MEAS = auto()


class Qubit(CavyType):

    def __init__(self, index: int):
        assert index >= 0
        self.index = index
        self.state = QubitState.LIVE

    def __eq__(self, other: 'Qubit') -> bool:
        return isinstance(other, Qubit) and self.index == other.index

    def __repr__(self) -> str:
        return f"<Qubit {self.index}>"

    def __hash__(self) -> int:
        return hash(self.index)


class QubitMeasurement(CavyType):
    """A counterpart to the Qubit class above; the corresponding post-measurement
    type
    """

    def __init__(self, index: int):
        assert index >= 0
        self.index = index

    def __eq__(self, other: 'QubitMeasurement') -> bool:
        return isinstance(other, QubitMeasurement) and self.index == other.index

    def __repr__(self) -> str:
        return f"<MeasurementResult {self.index}>"

    def __hash__(self) -> int:
        return hash(self.index)
