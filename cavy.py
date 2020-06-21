import argparse
from contextlib import redirect_stderr
import datetime
from enum import Enum, auto
from io import StringIO
import json
from pprint import pprint
import os
import re
import sys
from traceback import print_tb
from typing import Tuple, Optional

import dependencies as deps
from environment import UnboundNameError
from errors import CavyRuntimeError
from lexer import Lexer, LexError
from lang_token import Location, Token
from lang_parser import Parser, ParseError, s_expr
from interpreter import Interpreter
import config

GREETING = """
Welcome to the alpha version of this repl and language.
We hope that you enjoy your stay.
You can type ':q' to quit, and ':h' for help.
"""

HELP = """
TODO
"""

GOODBYE = """
Thanks for hacking with us!
"""

CONTACT_DEVELOPER = f"""Interpreter error: please contact the developer.

It will be helpful to send the crash log at `{config.CRASHLOG}`.
However, be advised that this file includes your entire input history for this session.
"""

UNICODE_SUPPORT = sys.stdout.encoding.lower().startswith('utf')
if UNICODE_SUPPORT:
    PROMPT = "ψ⟩ "
else:
    PROMPT = "> "


def init_argparse() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--debug', action='store_true')
    argparser.add_argument('script', nargs='?')
    return argparser


def pprint_lex_error(err: Tuple[Location, str]):
    location, message = err
    print("Lexing error: {} @ col:{}".format(message, location.column))


def pprint_parse_error(err: Tuple[Token, str]):
    token, message = err
    print("Parse error: {} @ col:{}".format(message, token.location.column))


def stack_trace(err: Exception) -> str:
    """For debugging: get a stack trace as a string
    """
    trace = StringIO()
    with redirect_stderr(trace):
        print_tb(err.__traceback__)
    return trace.getvalue()


def git_commit() -> Optional[str]:
    """For debugging: get the commit that the user is on, without external
    dependencies. Do this conservatively, because the git repo could be
    arbitrarily broken. You should always be able to fail and return `None`.
    """
    head_path = os.path.join(config.GIT_DIR, 'HEAD')
    try:
        with open(head_path, 'r') as f:
            head_contents = f.readline().strip()
            pattern = re.compile('ref:\s*(\S.*)')
            if (match := pattern.match(head_contents)):
                ref_path = os.path.join(config.GIT_DIR, match.group(1))
            else:
                # no ref: return nothing
                return None
        with open(ref_path, 'r') as f:
            # the happy path: read a hash from this ref and return it.
            return f.readline().strip()
    except FileNotFoundError:
        return None


class Repl:
    def __init__(self, debug=False):
        self.interpreter = Interpreter()
        self.history = []
        self.debug = debug

    def interact(self):
        print(GREETING)
        while True:
            try:
                print(PROMPT, end='')
                try:
                    line = input()
                except EOFError:
                    line = ':q'
                self.history.append(line)

                # special repl commands
                if line == ':q':
                    print(GOODBYE)
                    break
                elif line == ':h':
                    print(HELP)
                    continue
                elif line == ':e':
                    # cause an interpreter error
                    raise Exception("Raised a manual error")
                elif line == ':cirq':
                    # compile and print the circuit with Cirq.
                    self.print_cirq_circuit()
                    continue
                elif line == ':debug':
                    breakpoint()

                # now, eval the line
                lexer = Lexer(line)
                tokens = lexer.lex()
                if (errors := lexer.errors):
                    for err in errors:
                        pprint_lex_error(err)
                    continue
                parser = Parser(tokens)
                # parse the line as a statement
                stmt = parser.declaration()
                if not stmt:
                    for err in parser.errors:
                        pprint_parse_error(err)
                    continue
                self.interpreter.execute(stmt)

            except CavyRuntimeError as err:
                print(err)

            except KeyboardInterrupt:
                # This exception must be handled separately, as it should only
                # quit the repl. raise it to the very top.
                raise KeyboardInterrupt

            except Exception as err:
                # display the exception
                print(CONTACT_DEVELOPER)
                if self.debug:
                    print(stack_trace(err))
                    print(err)
                self.crash_report(err)

    def crash_report(self, err: Exception) -> None:
        """Dump error data to a log file."""

        # FIXME this solution could get slow if, for some reason, someone
        # suffers thousands of interpreter errors.
        report = {
            'history': self.history,
            'commit': git_commit(),
            'error': str(err),
            'traceback': stack_trace(err),
            'timestamp': str(datetime.datetime.now()),
        }
        try:
            with open(config.CRASHLOG, 'r') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        logs.append(report)
        with open(config.CRASHLOG, 'w') as f:
            json.dump(logs, f)

    @deps.require('cirq')
    def print_cirq_circuit(self):
        circuit = self.interpreter.circuit.to_cirq()
        print(circuit)


def interpret_script(script_path: str):
    with open(script_path, 'r') as f:
        script = f.read()
    tokens = Lexer(script).lex()
    statements = Parser(tokens).parse()
    Interpreter().interpret(statements)


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
