from typing import Any, List

from environment import Environment
from lang_token import TokenType
from lang_ast import *


class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self):
        self.environment = Environment()

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
            return not right

    def visit_literal(self, expr: Literal) -> Any:
        return expr.literal.data

    def visit_group(self, expr: Group) -> Any:
        return self.evaluate(expr.expr)

    def visit_variable(self, expr: Variable) -> Any:
        # TODO error handling
        return self.environment[expr]

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
        if self.evaluate(stmt.cond):
            self.execute(stmt.then_branch)
            return
        if (else_branch := stmt.else_branch):
            self.execute(else_branch)

    def evaluate(self, expr: Expression) -> Any:
        return expr.accept(self)

    # Because of Python's dynamic typing, `execute` actually does exactly the
    # same thing as `evaluate`. The distinction is preserved as a usage hint.
    def execute(self, stmt: Statement) -> None:
        return stmt.accept(self)

    def execute_blockstmt(self, stmts: List[Statement], env: Environment) -> None:
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
