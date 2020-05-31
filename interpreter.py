from typing import Any, List

from lang_token import TokenType
from lang_ast import *


class Interpreter(ExprVisitor, StmtVisitor):

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

    def visit_exprstmt(self, stmt: ExprStmt) -> None:
        self.evaluate(stmt.expr)

    def visit_printstmt(self, stmt: PrintStmt) -> None:
        value = self.evaluate(stmt.expr)
        print(value)

    def evaluate(self, expr: Expression) -> Any:
        return expr.accept(self)

    # Because of Python's dynamic typing, `execute` actually does exactly the
    # same thing as `evaluate`. The distinction is preserved as a usage hint.
    def execute(self, stmt: Statement) -> None:
        return stmt.accept(self)

    def interpret(self, statements: List[Statement]) -> None:
        for stmt in statements:
            self.execute(stmt)
