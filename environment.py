from lang_token import Token
from lang_ast import Variable

from typing import Any

class Environment:
    def __init__(self, enclosing=None, **defaults):
        self.values = {}
        self.enclosing = enclosing
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

    def __getitem__(self, var: Variable):
        # TODO Error handling
        try:
            return self.values[var.name.data]
        except KeyError as err:
            # Is this assignment expression actually an optimization?
            if (encl := self.enclosing):
                return encl[var]
            else:
                raise err
