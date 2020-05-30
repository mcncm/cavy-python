from pprint import pprint
import sys
from typing import Tuple

from lexer import Lexer, LexError
from lang_token import Location, Token
from lang_parser import Parser, ParseError, s_expr

UNICODE_SUPPORT = sys.stdout.encoding.lower().startswith('utf')
if UNICODE_SUPPORT:
    PROMPT = "ψ⟩ "
else:
    PROMPT = "> "


def pprint_lex_error(err: Tuple[Location, str]):
    location, message = err
    print("Lexing error: {} @ col:{}".format(message, location.column))


def pprint_parse_error(err: Tuple[Token, str]):
    token, message = err
    print("Parse error: {} @ col:{}".format(message, token.location.column))


def interact():
    while True:
        print(PROMPT, end='')
        line = input()

        if line == ':q':
            break

        lexer = Lexer(line)
        tokens = lexer.lex()
        if (errors := lexer.errors):
            for err in errors:
                pprint_lex_error(err)
            continue

        parser = Parser(tokens)
        ast = parser.parse()
        if not ast:
            for err in parser.errors:
                pprint_parse_error(err)
            continue
        pprint(s_expr(ast))


if __name__ == '__main__':
    if sys.stdin.isatty():
        interact()
        exit(0)
    else:
        exit(1)
