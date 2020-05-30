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


def test_keyword():
    """Ensure that keywords and identifiers are lexed properly"""
    code = 'if 2 thing'
    lexer = Lexer(code)
    tokens = lexer.lex()

    assert len(tokens) == 4
    assert len(lexer.errors) == 0

    kw = tokens[0]
    num = tokens[1]
    ident = tokens[2]

    assert kw.tokentype == TokenType.IF

    assert num.tokentype == TokenType.INT
    assert num.data == 2

    assert ident.tokentype == TokenType.IDENT
    assert ident.data == 'thing'


def test_fail():
    """Check that a nonexistent operator doesn't lex"""
    code = '<=='
    lexer = Lexer(code)
    tokens = lexer.lex()

    assert len(lexer.errors) > 0


def token_test_template(code, token_types):
    lexer = Lexer(code)
    tokens = lexer.lex()
    tokens.pop(-1)  # ignore eof
    lexed_token_types = list(map(lambda t: t.tokentype, tokens))

    assert len(lexed_token_types) == len(token_types)

    for (lexed_tt, spec_tt) in zip(lexed_token_types, token_types):
        assert lexed_tt == spec_tt


example_complex_code = "(12)+ *<- IdEnT;"
token_types = list(
    map(lambda s: getattr(TokenType, s), [
        'LPAREN', 'INT', 'RPAREN', 'PLUS', 'STAR', 'LESSMINUS', 'IDENT',
        'SEMICOLON'
    ]))


def test_complex_code():
    token_test_template(example_complex_code, token_types)
