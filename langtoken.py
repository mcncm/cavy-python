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

    # literals
    INT = auto()

    # two-character token types
    EQUALEQUAL = auto()
    LESSMINUS = auto()

    # single-character token types
    PLUS = auto()
    STAR = auto()
    BANG = auto()
    SEMICOLON = auto()

    # delimiters
    LBRACKET = auto()
    RBRACKET = auto()
    LPAREN = auto()
    RPAREN = auto()

    # end of file
    EOF = auto()

KEYWORDS = {
    'if': TokenType.IF,
    'for': TokenType.FOR,
}

class Token:
    """A lexical item"""

    def __init__(self, tokentype: TokenType, location: Location, data=None):
        self.tokentype = tokentype
        self.location = location
        self.data = data
