"""
A few small helper functions for compiling Cavy source.
"""

from circuits.circuit import Circuit
from interpreter import Interpreter
from lang_parser import Parser
from lexer import Lexer
from errors import CavyRuntimeError

class Program:

    def __init__(self, source: str):
        lexer = Lexer(source)
        tokens = lexer.lex()
        if (errors := lexer.errors):
            for err in errors:
                # TODO this is temporarily here so I can see what’s in `errors`
                breakpoint()
        parser = Parser(tokens)
        #
        # parse the line as a statement
        self.stmts = parser.parse()
        if not self.stmts:
            for err in parser.errors:
                # TODO this is temporarily here so I can see what’s in `errors`
                breakpoint()

    def compile(self) -> Circuit:
        """Note that we are somewhat mixing notions of 'compile-time' and 'runtime'.
        This method transforms the AST into Pycavy's Circuit data structure.
        """
        interpreter = Interpreter()
        try:
            interpreter.interpret(self.stmts)
        except CavyRuntimeError as err:
            print(err)
        return interpreter.circuit
