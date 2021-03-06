"""Syntax tree types. The generation of these types is to be regarded as an
implementation detail; the node types themselves are re-exported in
lang_ast.py.
"""

from abc import ABC, abstractmethod
from dataclasses import make_dataclass
from typing import Dict, Type, List

from lang_token import Token
from lang_types import CavyType


class AstNode:
    pass


class Expression(AstNode):
    pass


class Declaration(AstNode):
    pass


class Statement(Declaration):
    pass


def visit_method_name(node: str):
    return 'visit_{}'.format(name.lower())


def node_class(name: str, fields: Dict[str, Type], base):
    method_name = visit_method_name(name)

    def accept(self, visitor: 'Visitor'):
        return getattr(visitor, method_name)(self)

    namespace = {'accept': accept}
    return make_dataclass(name,
                          fields.items(),
                          bases=(base, ),
                          namespace=namespace)


# Here are the node types we'll use. Because we wish to automatically populate
# the Visitor interface, we will generate these classes dynamically.
EXPR_NODES = {
    'BinOp': {
        'left': Expression,
        'op': Token,
        'right': Expression,
    },
    'UnOp': {
        'op': Token,
        'right': Expression,
    },
    'Literal': {
        'literal': Token,
    },
    'Group': {
        'expr': Expression,
    },
    'Variable': {
        'name': Token,
    },
    'ExtensionalArray': {
        'items': List[Expression],
        'bracket': Token,
    },
    'IntensionalArray': {
        'item': Expression,
        'reps': Expression,
        'bracket': Token,
    },
    'Index': {
        'root': Expression,
        'index': Expression,
        'bracket': Token,
    },
    'Call': {
        'callee': Expression,
        'args': List[Expression],
        'paren': Token,
    }
}

STMT_NODES = {
    'ExprStmt': {
        'expr': Expression,
    },
    'PrintStmt': {
        'expr': Expression,
    },
    'AssnStmt': {
        'lhs': Token,
        'rhs': Expression,
    },
    'BlockStmt': {
        'stmts': List[Statement]
    },
    'IfStmt': {
        'cond': Expression,
        'then_branch': Statement,
        'else_branch': Statement,
    },
    'LetStmt': {
        'binder': Token,
        'expr': Expression,
        'body': Statement,
    },
    'ForStmt': {
        'binder': Token,
        'iterator': Expression,
        'body': Statement,
    },
    'FnStmt': {
        'name': Token,
        'params': List[Token],
        'body': Statement,
    },
}

# Generate the expression node classes
expr_abc_namespace = {}
for name, fields in EXPR_NODES.items():
    globals()[name] = node_class(name, fields, Expression)
    expr_abc_namespace[visit_method_name(name)] = abstractmethod(lambda: None)
ExprVisitor = type('ExprVisitor', (ABC, ), expr_abc_namespace)

stmt_abc_namespace = {}
for name, fields in STMT_NODES.items():
    globals()[name] = node_class(name, fields, Statement)
    stmt_abc_namespace[visit_method_name(name)] = abstractmethod(lambda: None)
StmtVisitor = type('ExprVisitor', (ABC, ), stmt_abc_namespace)
