"""
A few small helper functions for compiling Cavy source.
"""

from circuits.circuit import Circuit
from interpreter import Interpreter
from lang_parser import Parser
from lexer import Lexer
from errors import CavyRuntimeError

def compile(source: str, backend=None, opt: int = 0):
    """This function can be used to compile Cavy source to a chosen backend."""
    lexer = Lexer(source)
    interpreter = Interpreter()
    try:
        tokens = lexer.lex()
        if (errors := lexer.errors):
            for err in errors:
                # TODO this is temporarily here so I can see what’s in `errors`
                breakpoint()
        parser = Parser(tokens)
        #
        # parse the line as a statement
        stmts = parser.parse()
        if not stmts:
            for err in parser.errors:
                # TODO this is temporarily here so I can see what’s in `errors`
                breakpoint()
        interpreter.interpret(stmts)
    except CavyRuntimeError as err:
        print(err)

    circuit = interpreter.circuit
    return circuit.to_backend(backend)
