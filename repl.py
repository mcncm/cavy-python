from contextlib import redirect_stderr
import datetime
from io import StringIO
import json
import os
import re
import sys
from traceback import print_tb
from typing import Tuple, Optional

import dependencies as deps
from errors import CavyRuntimeError
from lang_token import Location, Token
from interpreter import Interpreter
from lexer import Lexer
from lang_parser import Parser
import config


GREETING = """
Welcome to the alpha version of this repl and language.
We hope that you enjoy your stay.
You can type ':q' to quit, and ':h' for help.
"""

HELP = f"""
If you have any problems with the language, or have any questions,
feel free to open an issue at '{config.REPO_URL}'
or email the developer at '{config.HELP_ADDRESS}'
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
                if line in [':q', ':quit']:
                    print(GOODBYE)
                    break
                elif line in [':h', ':help']:
                    print(HELP)
                    continue
                elif line in [':e', ':error']:
                    # cause an interpreter error
                    raise Exception("Raised a manual error")
                elif (line_args := line.split())[0] == ':cirq':
                    # compile and print the circuit with Cirq.
                    self.print_cirq_circuit(*line_args[1:])
                    continue
                elif self.debug and (line_args := line.split())[0] == ':qasm':
                    # compile and print the circuit as QASM.
                    circuit = self.interpreter.circuit
                    print(circuit.to_qasm())
                    continue
                elif (line_args := line.split())[0] == ':debug':
                    if len(line_args) == 1:
                        breakpoint()
                    else:
                        env_values = self.interpreter.environment.values
                        values = [env_values[name] for name in line_args[1:]]
                        print(*values)
                    continue

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
            'py_version': sys.version,
            'dependency_versions': {
                dep: deps.dependency_version(dep)
                    for dep in deps.LOADED_DEPENDENCIES
            },
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

    def print_cirq_circuit(self, *args):
        """Either print a cirq circuit to stdout, or convert it to LaTeX and write it to
        a file.

        TODO debug this function
        """
        circuit = self.interpreter.circuit
        if len(args) == 0:
            print(circuit.to_cirq())
        else:
            raise NotImplementedError
            # filename = args[0]
            # circuit.to_diagram(filename)
