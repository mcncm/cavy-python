from lang_token import TokenType
from lang_ast import *

class Interpreter(Visitor):

    def visit_binop(self, expr: BinOp):
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

    def visit_unop(self, expr: UnOp):
        right = self.evaluate(expr.right)

        token_type = expr.op.token_type
        if token_type == TokenType.TILDE:
            return not right

    def visit_literal(self, expr: Literal):
        return expr.literal.data

    def visit_group(self, expr: Group):
        return self.evaluate(expr.expr)

    def evaluate(self, expr: Expression):
        return expr.accept(self)

