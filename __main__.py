import argparse
import sys

from interpreter import Interpreter
from lexer import Lexer
from lang_parser import Parser
from repl import Repl, GOODBYE


def interpret_script(script_path: str):
    with open(script_path, 'r') as f:
        script = f.read()
    tokens = Lexer(script).lex()
    statements = Parser(tokens).parse()
    Interpreter().interpret(statements)


def init_argparse() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--debug', action='store_true')
    argparser.add_argument('script', nargs='?')
    return argparser


if __name__ == '__main__':
    if not sys.stdin.isatty():
        exit(1)

    argparser = init_argparse()
    args_ns = argparser.parse_args(sys.argv[1:])

    if args_ns.script:
        try:
            interpret_script(args_ns.script)
        except FileNotFoundError:
            print(f"Error: no file {args_ns.script} found")
        exit(0)

    try:
        Repl(debug=args_ns.debug).interact()
        exit(0)
    except KeyboardInterrupt:
        print(GOODBYE)
