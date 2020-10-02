from abc import ABC, abstractmethod

from environment import Environment


class AbstractFunction(ABC):
    arity = 0

    @abstractmethod
    def call(self, args):
        pass


class Function(AbstractFunction):

    def __init__(self, params, body):
        self.params = params
        self.arity = len(self.params)
        self.body = body

    def call(self, interp, args):
        env = Environment(interp.environment)
        for param, arg in zip(self.params, args):
            env.set_key_value(param.data, arg)
        interp.execute_blockstmt(
            self.body.stmts,
            env
        )
