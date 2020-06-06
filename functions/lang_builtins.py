from environment import Environment
from .function import Function


class Qubit(Function):
    """Allocates and returns a single qubit"""
    arity = 0

    def call(self, env: Environment, args):
        raise NotImplementedError


class Split(Function):
    """Implements a logical Hadamard operation on a single qubit"""
    arity = 1

    def call(self, env: Environment, args):
        raise NotImplementedError


class Phase(Function):
    """Implements a logical phase gate on a single qubit"""
    arity = 2

    def call(self, env: Environment, args):
        raise NotImplementedError


class Debug(Function):
    """A debug function that prints a debug message"""
    arity = 1

    def call(self, env: Environment, args):
        print(f"Called `debug` with flag {args[0]}")
