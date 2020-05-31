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
        self.history = []
        self.debug = debug

    def interact(self):
        print(GREETING)
        while True:
            try:
                print(PROMPT, end='')
                line = input()
                self.history.append(line)

                # special repl commands
                if line == ':q':
                    print(GOODBYE)
                    break
                if line == ':h':
                    print(HELP)
                    continue
                if line == ':e':
                    # cause an interpreter error
                    raise Exception("Raised a manual error")

                # eval the line
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
                interpreter = Interpreter()
                res = interpreter.evaluate(ast)
                print(res)

            except KeyboardInterrupt:
                # This exception must be handled separately, as it should only
                # quit the repl. raise it to the very top.
                raise KeyboardInterrupt
            except Exception as err:
                # display the exception
                print(CONTACT_DEVELOPER)
                if self.debug:
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


if __name__ == '__main__':
    if sys.stdin.isatty():
        try:
            argparser = init_argparse()
            args_ns = argparser.parse_args(sys.argv[1:])
            Repl(debug=args_ns.debug).interact()
        except KeyboardInterrupt:
            print(GOODBYE)
        exit(0)
    else:
        exit(1)
