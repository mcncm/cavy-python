from enum import Enum, auto
from typing import Any, List

from circuits.circuit import Circuit
from circuits.gates import Gate
from errors import CavyRuntimeError
from lang_token import Token
from lang_ast import Variable
from lang_types import Qubit


class UnboundNameError(CavyRuntimeError):
    """Raised when a name is referenced that is not bound to anything in the
    current scope."""
    def __str__(self):
        return f"Unbound name error: either '{self.args[0]}' has not been "\
               "assigned, or its contents have been moved."


class NoopAllocator:
    """A trivial allocator that I'll use for the time being. Because we assumed
    that qubits can't be reinitialized, freeing is a no-op."""
    def __init__(self):
        self.least_free = 0
        self.freed = set()

    def __contains__(self, num: int) -> bool:
        return num < self.least_free and num not in self.freed

    def alloc_one(self) -> int:
        new = self.least_free
        self.least_free += 1
        return new

    def free_one(self, num: int) -> None:
        """Do nothing but add it to a freed list"""
        assert num in self
        self.freed.add(num)


class Environment:
    def __init__(self, enclosing=None, control=None, **defaults):
        self.values = {}
        self.qubits = NoopAllocator()
        self.enclosing = enclosing
        self.control = control
        for name, default_value in defaults.items():
            self.set_key_value(name, default_value)

    def __setitem__(self, var: Variable, value: Any):
        # var.name.data contains the actual variable name string
        name = var.name.data
        scope = self
        while scope is not None:
            if name in scope.values:
                scope.set_key_value(name, value)
                return
            scope = scope.enclosing
        # default case: no reference found in any enclosing environment
        self.set_key_value(name, value)

    def set_key_value(self, name: str, value: Any):
        self.values[name] = value

    def alloc_one(self) -> Qubit:
        index = self.qubits.alloc_one()
        return Qubit(index)

    def embed_gate(self, gate: Gate) -> List[Gate]:
        """Embed a block-local gate as a list of gates in the global scope."""
        if self.control is not None:
            gates = gate.with_control(self.control)
        else:
            gates = [gate]
        if self.enclosing:
            enclosing_gates = [self.enclosing.embed_gate(gate) for gate in gates]
            # flatten this list: TODO better in one list comprehension?
            gates = [gate for gates_ in enclosing_gates for gate in gates_]
        return gates

    def __getitem__(self, var: Variable):
        # TODO Error handling
        name = var.name.data
        try:
            value = self.values[name]
            # The value is a quantum state: remove it from the environment!
            if isinstance(value, Qubit):
                self.values.pop(name)
                return value
            else:
                return value
        except KeyError as err:
            if (encl := self.enclosing):
                return encl[var]
            else:
                raise UnboundNameError(name)
