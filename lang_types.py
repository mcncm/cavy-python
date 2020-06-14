from enum import Enum, auto


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
        return self.index == other.index

    def __repr__(self) -> str:
        return f"<Qubit {index}>"

    def __hash__(self) -> int:
        return hash(self.index)
