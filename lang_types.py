from enum import Enum, auto
from typing import Any, List


class OrderedEnum(Enum):
    """An enumeration with a total order by value on its alternatives."""

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value


class TypingDiscipline(OrderedEnum):
    UNRESTRICTED   = 0
    AFFINE         = 1
    LINEAR         = 2
    NONCOMMUTATIVE = 3


def _get_discipline(value):
    try:
        return value._discipline
    except AttributeError:
        return TypingDiscipline.UNRESTRICTED


def is_linear(value):
    return _get_discipline(value) >= TypingDiscipline.LINEAR


class CavyType:

    @property
    def discipline(self):
        return _get_discipline(self)


class Qubit(CavyType):

    _discipline = TypingDiscipline.LINEAR

    def __init__(self, index: int):
        assert index >= 0
        self.index = index

    def __eq__(self, other: 'Qubit') -> bool:
        return isinstance(other, Qubit) and self.index == other.index

    def __repr__(self) -> str:
        return f"<Qubit {self.index}>"

    def __hash__(self) -> int:
        return hash(self.index)


class Array(CavyType):

    def __init__(self, values: List):
        self._discipline = max(map(_get_discipline, values))
        self.values = values

    def __getitem__(self, index: int):
        return self.values[index]

    def __iter__(self):
        return iter(self.values)


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
