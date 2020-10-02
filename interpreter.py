from typing import Any, List

from circuits.circuit import Circuit
import circuits.gates as gates
from environment import Environment
from functions import BUILTINS, AbstractFunction, Function
from lang_ast import *
from lang_token import TokenType
from lang_types import Qubit


class InterpreterError(Exception):
    pass


class _TypeError(InterpreterError):
    pass


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.environment = Environment(**BUILTINS)
        self.circuit = Circuit()

    def visit_binop(self, expr: BinOp) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        token_type = expr.op.token_type
        if token_type == TokenType.PLUS:
            return left + right
        elif token_type == TokenType.STAR:
            return left * right
        elif token_type == TokenType.EQUALEQUAL:
            return left == right
        elif token_type == TokenType.TILDEEQUAL:
            return left != right

    def visit_unop(self, expr: UnOp) -> Any:
        right = self.evaluate(expr.right)
        token_type = expr.op.token_type

        if token_type == TokenType.TILDE:
            if isinstance(right, Qubit):
                gates_ = self.environment.embed_gate(
                    gates.NotGate(right.index))
                self.circuit.add_gates(gates_)
                return right
            else:
                return not right

        elif token_type == TokenType.QUESTION:
            if isinstance(right, bool):
                # Stack-allocate a brand new qubit
                qubit = self.environment.alloc_one()
                if right:
                    gates_ = self.environment.embed_gate(
                        gates.NotGate(qubit.index)
                    )
                    self.circuit.add_gates(gates_)
                return qubit
            else:
                breakpoint()
                # TODO Figure out how to get a location out of expr
                raise InterpreterError(
                    0,
                    f"The value '{right}' cannot be linearized."
                )

        elif token_type == TokenType.BANG:
            # TODO Need measurement operator
            if isinstance(right, Qubit):
                pass
                return False;
            else:
                # TODO Figure out how to get a location out of expr
                raise InterpreterError(
                    0,
                    f"The value '{right}' cannot be delinearized"
                )

    def visit_literal(self, expr: Literal) -> Any:
        return expr.literal.data

    def visit_group(self, expr: Group) -> Any:
        return self.evaluate(expr.expr)

    def visit_variable(self, expr: Variable) -> Any:
        # TODO error handling
        return self.environment[expr]

    def visit_call(self, expr: Call) -> Any:
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, AbstractFunction):
            raise _TypeError(f"{callee} not a function")
        args = [self.evaluate(arg) for arg in expr.args]
        if len(args) != callee.arity:
            raise InterpreterError(
                expr.paren,
                f"Function takes {callee.arity} arguments; got {len(args)}.")
        return callee.call(self, args)

    def visit_exprstmt(self, stmt: ExprStmt) -> None:
        self.evaluate(stmt.expr)

    def visit_printstmt(self, stmt: PrintStmt) -> None:
        value = self.evaluate(stmt.expr)
        print(value)

    def visit_assnstmt(self, stmt: AssnStmt) -> None:
        value = self.evaluate(stmt.rhs)
        self.environment[Variable(stmt.lhs)] = value

    def visit_blockstmt(self, stmt: BlockStmt) -> None:
        self.execute_blockstmt(stmt.stmts, Environment(self.environment))
        return None

    def visit_ifstmt(self, stmt: IfStmt) -> None:
        # TODO decide what must be truthy and what falsey.
        cond_value = self.evaluate(stmt.cond)

        # TODO replace this check with a check on the linearity of the
        # value's type
        if isinstance(cond_value, Qubit):
            if not isinstance(
                    stmt.cond,
                    Variable):  # this is my *only* allowed case for now
                raise NotImplementedError
            # The visitor pattern is broken here. This seems, though, to be the
            # easiest way to pass in the control data, and it should be
            # guaranteed by the parser that this is a block statement.
            control = cond_value.index
            self.execute_blockstmt(
                stmt.then_branch.stmts,
                Environment(self.environment, control=control))
            # Re-bind the variable: this is actually the absolutely right way
            # to do this, because you shouldn't be able to name this value
            # within the inner scope.
            self.environment[stmt.cond] = cond_value

        # classical type: this is an "ordinary" `if` statement
        else:
            if cond_value:
                self.execute(stmt.then_branch)
                return
            if (else_branch := stmt.else_branch):
                self.execute(else_branch)

    def visit_fnstmt(self, stmt: FnStmt) -> None:
        """Define a function!
        """
        self.environment[Variable(stmt.name)] = Function(stmt.params, stmt.body)

    def evaluate(self, expr: Expression) -> Any:
        return expr.accept(self)

    # Because of Python's dynamic typing, `execute` actually does exactly the
    # same thing as `evaluate`. The distinction is preserved as a usage hint.
    def execute(self, stmt: Statement) -> None:
        return stmt.accept(self)

    def execute_blockstmt(self, stmts: List[Statement],
                          env: Environment) -> None:
        # TODO consider changing the Environment implementation to be a context
        # manager.
        prev = self.environment
        self.environment = env
        try:
            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.environment = prev

    def interpret(self, statements: List[Statement]) -> None:
        for stmt in statements:
            self.execute(stmt)
