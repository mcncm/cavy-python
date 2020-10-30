"""A top-down parser generating an AST for pyqlang, closely following the Lox
reference parser.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from lang_token import Token, TokenType, Location
from lang_ast import *

MAX_ARGS = 64

# Fields mean: precedence, is_right_associative
OPERATOR_TABLE = {
    TokenType.TILDEEQUAL: (1, False),
    TokenType.EQUALEQUAL: (1, False),
    TokenType.STOPSTOP:   (2, False),
    TokenType.PLUS:       (3, False),
    TokenType.MINUS:      (3, False),
    TokenType.STAR:       (4, False),
    TokenType.PERCENT:    (4, False),
    TokenType.CARET:      (5, True),
}


@dataclass
class ParseError(Exception):
    token: Token
    message: str


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
    else:
        raise NotImplementedError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0  # scan head position in token stream
        self.errors = []  # a buffer that fills up as parse errors are found

    # Helper methods

    def error(self, token: Token, message: str):
        raise ParseError(token, message)

    def prev(self):
        assert self.pos > 0
        return self.tokens[self.pos - 1]

    def curr(self):
        return self.tokens[self.pos]

    def next(self):
        assert self.pos < len(self.tokens) - 1
        return self.tokens[self.pos + 1]

    def at_end(self):
        return self.curr().token_type == TokenType.EOF

    def forward(self) -> Token:
        if not self.at_end():
            self.pos += 1
        return self.prev()

    def check_token(self, token_type: TokenType) -> bool:
        """Return True if the token at the given index exists and is of the given
        type."""
        in_bounds = self.pos < len(self.tokens)
        return in_bounds and self.curr().token_type == token_type

    def match_tokens(self, *token_types: TokenType) -> bool:
        """Advance if the current token is one of this list"""
        if any(self.check_token(tt) for tt in token_types):
            self.forward()
            return True
        return False

    def match_token_sequence(self, *token_types: TokenType) -> bool:
        """Advance if the following tokens are exactly this list, in order."""
        saved_pos = self.pos
        for tt in token_types:
            if not self.check_token(tt):
                self.pos = saved_pos
                return False
            self.forward()
        return True

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check_token(token_type):
            return self.forward()
        self.error(self.curr(), message)

    # Nonterminals

    def declaration(self) -> Optional[Statement]:
        try:
            if self.match_token_sequence(TokenType.IDENT, TokenType.LESSMINUS):
                return self.assignment()
            elif self.match_token_sequence(TokenType.FN, TokenType.IDENT):
                return self.function_definition()
            return self.statement()
        except ParseError as err:
            self.errors.append((err.token, err.message))
            self.synchronize()

    def function_definition(self) -> Statement:
       name =  self.tokens[self.pos - 1]
       params = []

       self.consume(TokenType.LPAREN,
                    "expected '(' at beginning of function parameters")

       if not self.check_token(TokenType.RPAREN):
           while True:
               param = self.consume(TokenType.IDENT,
                                    "expected identifier as function parameter")
               params.append(param)
               if not self.match_tokens(TokenType.COMMA):
                   break
       paren = self.consume(TokenType.RPAREN,
                            "missing ')' at end of arguments")

       self.consume(TokenType.LBRACE,
                    "missing '{' opening function body")

       body = self.block_statement()
       return FnStmt(name, params, body)

    def statement(self) -> Statement:
        if self.match_tokens(TokenType.IF):
            return self.if_statement()
        elif self.match_tokens(TokenType.LET):
            return self.let_statement()
        elif self.match_tokens(TokenType.FOR):
            return self.for_statement()
        elif self.match_tokens(TokenType.PRINT):
            return self.print_statement()
        elif self.match_tokens(TokenType.LBRACE):
            return self.block_statement()
        return self.expr_statement()

    def assignment(self) -> AssnStmt:
        """Production rule for assignment declarations. Because this lives under a
        `match_token_sequence`, we're assumed to be positioned at first token
        of the rhs.
        """
        lhs = self.tokens[self.pos - 2]
        rhs = self.expression()
        self.consume(TokenType.SEMICOLON, "missing ';' after expression")
        return AssnStmt(lhs, rhs)

    def if_statement(self) -> IfStmt:
        condition = self.expression()
        self.consume(TokenType.LBRACE,
                     "missing '{' opening direct branch of conditional")
        then_branch = self.block_statement()
        if self.match_tokens(TokenType.ELSE):
            self.consume(TokenType.LBRACE,
                         "missing '{' opening indirect branch of conditional")
            else_branch = self.block_statement()
        else:
            else_branch = None
        return IfStmt(condition, then_branch, else_branch)

    def let_statement(self) -> LetStmt:
        binder = self.consume(TokenType.IDENT, "expected an identifier to bind 'let' statement")
        self.consume(TokenType.LESSMINUS,
                     "expected '<-' in 'with' statement")
        expr = self.expression()
        self.consume(TokenType.IN,
                     "expexted 'in' in 'with' statement")
        self.consume(TokenType.LBRACE,
                     "missing '{' opening 'with' body")
        body = self.block_statement()
        return LetStmt(binder, expr, body)

    def for_statement(self) -> ForStmt:
        binder = self.consume(TokenType.IDENT, "expected an identifier to bind 'for' statement")
        self.consume(TokenType.IN, "expected 'in' in 'for' statement")
        iterator = self.expression()
        self.consume(TokenType.LBRACE,
                     "missing '{' opening loop body")
        body = self.block_statement()
        return ForStmt(binder, iterator, body)

    def print_statement(self) -> PrintStmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "missing ';' after expression")
        return PrintStmt(value)

    def block_statement(self) -> BlockStmt:
        statements = []
        while not self.check_token(TokenType.RBRACE) and not self.at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RBRACE, "missing '}' at end of block")
        return BlockStmt(statements)

    def expr_statement(self) -> ExprStmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "missing ';' after expression")
        return ExprStmt(expr)

    def expression(self):
        lhs = self.unary()
        return self.parse_precedence_climbing(lhs, 0)

    def parse_precedence_climbing(self, lhs, min_precedence):
        while True:
            outer_token = self.curr()
            if outer_token.token_type not in OPERATOR_TABLE:
                break
            outer_precedence, _ = OPERATOR_TABLE[outer_token.token_type]
            if outer_precedence < min_precedence:
                break
            self.forward()
            rhs = self.unary()
            while True:
                inner_token = self.curr()
                if inner_token.token_type not in OPERATOR_TABLE:
                    break
                inner_precedence, right_associative = OPERATOR_TABLE[inner_token.token_type]
                # We break if inner_precedence == outer_precedence and right_associative.
                if inner_precedence < outer_precedence + (not right_associative):
                    break
                rhs = self.parse_precedence_climbing(rhs, inner_precedence)
            lhs = BinOp(lhs, outer_token, rhs)
        return lhs

    def unary(self) -> Expression:
        if self.match_tokens(TokenType.QUESTION, TokenType.BANG, TokenType.TILDE):
            op = self.prev()
            right = self.unary()
            return UnOp(op, right)
        elif self.match_tokens(TokenType.LBRACKET):
            return self.finish_array()
        else:
            return self.call()

    def finish_array(self):
        """Finish parsing an array, where the opening bracket has already been consumed
        """

        def closing_bracket():
            return self.consume(TokenType.RBRACKET, "mising ']' at end of array")

        head = self.expression()
        if self.match_tokens(TokenType.COMMA):
            items = []
            while True:
                items.append(self.expression())
                if not self.match_tokens(TokenType.COMMA):
                    break
            items.insert(0, head)
            return ExtensionalArray(items, closing_bracket())
        elif self.match_tokens(TokenType.SEMICOLON):
            reps = self.expression()
            return IntensionalArray(head, reps, closing_bracket())
        else:
            # NOTE what happens in this case? Does the parser know what to do?
            self.error(self.curr(), "Expected ',' or ';' in array.")

    def call(self):
        """Call a function or index into an array
        """
        expr = self.primary()
        while True:
            if self.match_tokens(TokenType.LPAREN):
                expr = self.finish_call(expr)
            elif self.match_tokens(TokenType.LBRACKET):
                expr = self.finish_index(expr)
            else:
                break
        return expr

    def finish_call(self, callee: Expression):
        args = []
        if not self.check_token(TokenType.RPAREN):
            while True:
                if len(args) >= MAX_ARGS:
                    self.error(self.curr(),
                               "maximum number of arguments exceeded")
                args.append(self.expression())
                if not self.match_tokens(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RPAREN, "missing ')' at end of arguments")
        return Call(callee, args, paren)

    def finish_index(self, root):
        index = self.expression()
        bracket = self.consume(TokenType.RBRACKET, "missing ']' at end of index expression")
        return Index(root, index, bracket)

    def primary(self) -> Optional[Expression]:
        if self.match_tokens(TokenType.INT, TokenType.BOOL):
            return Literal(self.prev())
        elif self.match_tokens(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "missing ')'")
            return Group(expr)
        elif self.match_tokens(TokenType.IDENT):
            return Variable(self.prev())
        self.error(self.curr(), "expression expected")

    def synchronize(self) -> None:
        self.forward()
        while not self.at_end():
            if self.prev().token_type == TokenType.SEMICOLON:
                return

        barriers = [TokenType.IF, TokenType.FOR, TokenType.FN]
        if self.curr().token_type in barriers:
            return
        self.forward()

    def parse(self) -> List[Statement]:
        statements = []
        while not self.at_end():
            if (decl := self.declaration()):
                statements.append(decl)
        return statements
