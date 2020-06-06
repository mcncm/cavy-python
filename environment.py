from lang_token import Token
from lang_ast import Variable

from typing import Any

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def __setitem__(self, var: Variable, value: Any):
        # var.name.data contains the actual variable name string
        name = var.name.data
        scope = self
        while scope.enclosing is not None:
            if name in scope.values:
                scope.values[name] = value
                return
            scope = scope.enclosing
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
