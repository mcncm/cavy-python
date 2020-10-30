from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Location:
    """Type for keeping track of the location of a source item"""
    position: int   # position from start of source
    line: int       # line number in source
    column: int     # column number in source
    length: int     # length of the item in characters


class TokenType(Enum):
    """Flag for keeping track of the type of a lexical element"""
    # identifiers
    IDENT = auto()

    # keywords
    IF = auto()
    ELSE = auto()
    FOR = auto()
    LET = auto()
    IN = auto()
    FN = auto()
    PRINT = auto()

    # literals
    INT = auto()
    BOOL = auto()

    # two-character token types
    STOPSTOP = auto()
    EQUALEQUAL = auto()
    TILDEEQUAL = auto()
    LESSMINUS = auto()

    # single-character token types
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    PERCENT = auto()
    CARET = auto()
    QUESTION = auto()
    BANG = auto()
    TILDE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    # delimiters
    LBRACKET = auto()
    RBRACKET = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()

    # end of file
    EOF = auto()


class Token:
    """A lexical item"""

    def __init__(self, token_type: TokenType, location: Location, data=None):
        self.token_type = token_type
        self.location = location
        self.data = data

    def __repr__(self) -> str:
        data_part = f", data {self.data}" if self.data else ""
        return f"<Token: type {self.token_type.name}{data_part}>"
