"""Syntax tree types. The generation of these types is to be regarded as an
implementation detail; the node types themselves are re-exported in
lang_ast.py.
"""

from abc import ABC, abstractmethod
from dataclasses import make_dataclass
from typing import Dict, Type

from lang_token import Token


class AstNode:
    pass


class Expression(AstNode):
    pass


def visit_method_name(node: str):
    return 'visit_{}'.format(name.lower())


def gen_expr_class(name: str, fields: Dict[str, Type]):
    method_name = visit_method_name(name)

    def accept(self, visitor: 'Visitor'):
        return getattr(visitor, method_name)(self)

    namespace = {'accept': accept}
    return make_dataclass(name, fields.items(), namespace=namespace)


# Here are the node types we'll use. Because we wish to automatically populate
# the Visitor interface, we will generate these classes dynamically.
EXPR_NODES = {
    'BinOp': {
        'left': Expression,
        'op': Token,
        'right': Expression
    },
    'UnOp': {
        'op': Token,
        'right': Expression
    },
    'Literal': {
        'literal': Token
    },
    'Group': {
        'expr': Expression
    },
}

# Generate the expression node classes
abc_namespace = {}
for name, fields in EXPR_NODES.items():
    globals()[name] = gen_expr_class(name, fields)
    abc_namespace[visit_method_name(name)] = abstractmethod(lambda: None)

Visitor = type('Visitor', (ABC, ), abc_namespace)
