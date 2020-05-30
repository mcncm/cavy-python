import copy
from dataclasses import dataclass
from typing import *

from langtoken import Location, Token, TokenType, KEYWORDS


@dataclass
class LexError(Exception):
    location: Location
    message: str


class EndOfFile(Exception):
    pass


class ScanHead:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0  # character position in source
        self.line = 1  # currently scanned line number
        self.col = 0  # currently scanned source column

    def curr(self) -> Optional[str]:
        try:
            return self.code[self.pos]
        except IndexError:
            return None

    def forward(self) -> None:
        """Advance by one character"""
        if self.curr() == '\n':
            self.line += 1
            self.col = 0
        else:
            self.col += 1
        self.pos += 1

    def advance_to_whitespace(self) -> None:
        """advance until a whitespace character or eof"""
        while self.isnotspace():
            self.forward()

    # The following several methods lift boolean string methods to optional
    # strings. This feels unnecessarily manual, but I don't think Python offers
    # the language constructs I would like to use.
    def isalnum(self) -> bool:
        curr = self.curr()
        return curr and curr.isalnum()

    def isspace(self) -> bool:
        curr = self.curr()
        return curr and curr.isspace()

    def isnotspace(self) -> bool:
        curr = self.curr()
        return curr and not curr.isspace()


class Lexer:
    def __init__(self, code: str):
        self.code = code  # the source as a string
        self.tail = ScanHead(code)  # follower pointer
        self.head = ScanHead(code)  # leader pointer
        self.errors = []  # an error buffer that fills during lexing

    def location(self) -> Location:
        """Location of current token"""
        return Location(self.tail.pos, self.tail.line, self.tail.col,
                        self.head.pos - self.tail.pos)

    def error(self, message: str):
        """raise an error, to be handled up the stack by some recovery policy"""
        raise LexError(self.location(), message)

    def lex(self) -> List[Token]:
        """Produces a sequence of tokens from source code"""
        tokens = []
        while True:
            try:
                tokens.append(self.next_token())
            except LexError as err:
                self.errors.append((err.location, err.message))
                # We'll recover from every error by moving on to the next
                # whitespace character. This will get some false negatives: we
                # might miss some lexing errors this way. But in the worst
                # case, we can carry on at the next line.
                self.head.advance_to_whitespace()
            except EndOfFile:
                tokens.append(Token(TokenType.EOF, self.location()))
                break
        return tokens

    def token_chars(self) -> str:
        """Characters comprising the currently-scanned token"""
        return self.code[self.tail.pos:self.head.pos]

    def next_token(self) -> Token:
        """Consume another token!
        """
        # advance to the next token
        head = self.head
        while head.isspace():
            head.forward()
        # now ready to begin lexing the next token
        tail = self.tail = copy.copy(head)

        curr = head.curr()
        # eof: raise an exception to the lexing loop to break
        if curr is None:
            raise EndOfFile

        # identifiers and keywords
        if curr.isalpha():
            while head.isalnum():
                head.forward()
            val = self.token_chars()
            if (token_type := KEYWORDS.get(val)):
                token = Token(token_type, self.location())
            else:
                token = Token(TokenType.IDENT, self.location(), data=val)
            return token

        # integer literal
        elif curr.isdigit():
            while head.curr() and head.curr().isdigit():
                head.forward()
            if head.curr() and head.curr().isalpha():
                # We must have encountered something like `123abc`, which is an
                # illegal identifier name. Note the error; give up and continue
                # to the next whitespace, in the of finding more lexing errors.
                self.error("identifier cannot start with digits")
            else:
                # We must have a good integer literal! e.g. ` 123 `, `[2]`,
                # etc.
                val = int(self.token_chars())
                return Token(TokenType.INT, self.location(), data=val)

        # two-character operator tokens
        elif curr == '=':
            head.forward()
            if head.curr() == '=':
                head.forward()
                return Token(TokenType.EQUALEQUAL, self.location())
            else:
                self.error(f"undefined token `{self.token_chars()}`")

        elif curr == '!':
            head.forward()
            if head.curr() == '=':
                head.forward()
                return Token(TokenType.BANGEQUAL, self.location())
            else:
                return Token(TokenType.BANG, self.location())

        elif curr == '<':
            head.forward()
            if head.curr() == '-':
                head.forward()
                return Token(TokenType.LESSMINUS, self.location())
            else:
                self.error(f"undefined token `{self.token_chars()}`")

        # one-character operator and delimiter tokens
        elif curr == '+':
            head.forward()
            return Token(TokenType.PLUS, self.location())

        elif curr == '*':
            head.forward()
            return Token(TokenType.STAR, self.location())

        elif curr == '!':
            head.forward()
            return Token(TokenType.BANG, self.location())

        elif curr == ';':
            head.forward()
            return Token(TokenType.SEMICOLON, self.location())

        elif curr == '[':
            head.forward()
            return Token(TokenType.LBRACKET, self.location())

        elif curr == ']':
            head.forward()
            return Token(TokenType.RBRACKET, self.location())

        elif curr == '(':
            head.forward()
            return Token(TokenType.LPAREN, self.location())

        elif curr == ')':
            head.forward()
            return Token(TokenType.RPAREN, self.location())
