from abc import ABC, abstractmethod


class Function(ABC):
    arity = 0

    @abstractmethod
    def call(self, args):
        pass
