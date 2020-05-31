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
    FOR = auto()
    FN = auto()
    REG = auto()
    PRINT = auto()

    # literals
    INT = auto()
    BOOL = auto()

    # two-character token types
    EQUALEQUAL = auto()
    TILDEEQUAL = auto()
    LESSMINUS = auto()

    # single-character token types
    PLUS = auto()
    STAR = auto()
    BANG = auto()
    TILDE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    # delimiters
    LBRACKET = auto()
    RBRACKET = auto()
    LPAREN = auto()
    RPAREN = auto()

    # end of file
    EOF = auto()


class Token:
    """A lexical item"""

    def __init__(self, token_type: TokenType, location: Location, data=None):
        self.token_type = token_type
        self.location = location
        self.data = data
