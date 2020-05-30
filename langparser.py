"""A top-down parser generating an AST for pyqlang, closely following the Lox
reference parser.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from langtoken import Token, TokenType, Location


@dataclass
class ParseError(Exception):
    token: Token
    message: str


class AstNode:
    pass


class Expression(AstNode):
    pass


@dataclass
class BinOp(Expression):
    left: AstNode
    op: Token
    right: AstNode


@dataclass
class UnOp(Expression):
    op: Token
    right: AstNode


@dataclass
class Literal(Expression):
    literal: Token


@dataclass
class Group(Expression):
    expr: Expression


def s_expr(ast: Expression) -> Tuple:
    """Represent an AST as an S-expression
    """
    if isinstance(ast, BinOp):
        return (ast.op.token_type.name, s_expr(ast.left), s_expr(ast.right))
    elif isinstance(ast, UnOp):
        return (ast.op.token_type.name, s_expr(ast.right))
    elif isinstance(ast, Literal):
        return ast.literal.data
    elif isinstance(ast, Group):
        return s_expr(ast.expr)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    # Helper methods
    def error(self, token: Token, message: str):
        raise ParseError(token, message)

    def prev(self):
        assert self.pos > 0
        return self.tokens[self.pos - 1]

    def curr(self):
        return self.tokens[self.pos]

    def at_end(self):
        return self.curr().token_type == TokenType.EOF

    def forward(self) -> Token:
        if not self.at_end():
            self.pos += 1
        return self.prev()

    def check_token(self, token_type: TokenType) -> bool:
        return not self.at_end() and self.curr().token_type == token_type

    def match_tokens(self, *token_types: List[TokenType]) -> bool:
        if any([self.check_token(tt) for tt in token_types]):
            self.forward()
            return True
        return False

    def consume(self, token_type: TokenType, message: str):
        if self.check_token(token_type):
            return self.forward()
        self.error(self.curr(), message)

    # Nonterminals
    def expression(self):
        return self.equality()

    def equality(self) -> Expression:
        """Production rule for equality expressions
        """
        expr = self.comparison()
        while self.match_tokens(TokenType.TILDEEQUAL, TokenType.EQUALEQUAL):
            op = self.prev()
            right = self.comparison()
            expr = BinOp(expr, op, right)
        return expr

    def comparison(self) -> Expression:
        """Production rule for comparison expressions. We don't yet support these, so
        they go straight to the next-higher-precedence rule.
        """
        return self.addition()

    def addition(self) -> Expression:
        expr = self.multiplication()
        while self.match_tokens(TokenType.PLUS):
            op = self.prev()
            right = self.multiplication()
            expr = BinOp(expr, op, right)
        return expr

    def multiplication(self) -> Expression:
        expr = self.unary()
        while self.match_tokens(TokenType.STAR):
            op = self.prev()
            right = self.unary()
            expr = Binop(expr, op, right)
        return expr

    def unary(self) -> Expression:
        if self.match_tokens(TokenType.BANG, TokenType.TILDE):
            op = self.prev()
            right = self.unary()
            return UnOp(op, right)
        return self.primary()

    def primary(self) -> Expression:
        if self.match_tokens(TokenType.INT):
            return Literal(self.prev())
        if self.match_tokens(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "missing ')'")
            return Group(expr)
        self.error(self.curr(), "expression expected")

    def synchronize(self) -> None:
        self.forward()
        while not self.at_end():
            if self.prev().token_type == TokenType.SEMICOLON:
                return

        barriers = ['IF', 'FOR', 'FN']
        if self.curr().token_type in barriers:
            return
        self.forward()

    def parse(self) -> Optional[Expression]:
        try:
            return self.expression()
        except ParseError:
            return None
