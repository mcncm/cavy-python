from langtoken import TokenType

from lexer import Lexer

def test_simple():
    """Assert everything about a simple boolean expression"""

    code = '123 == 4567'
    lexer = Lexer(code)
    tokens = lexer.lex()

    assert len(tokens) == 4
    assert len(lexer.errors) == 0

    n1 = tokens[0]
    eq = tokens[1]
    n2 = tokens[2]
    eof = tokens[3]

    assert n1.tokentype == TokenType.INT
    assert n1.data == 123
    assert n1.location.position == 0
    assert n1.location.length == 3

    assert eq.tokentype == TokenType.EQUALEQUAL
    assert eq.location.position == 4
    assert eq.location.length == 2

    assert n2.tokentype == TokenType.INT
    assert n2.data == 4567
    assert n2.location.position == 7
    assert n2.location.length == 4

    assert eof.tokentype == TokenType.EOF
    assert eof.location.position == 11
