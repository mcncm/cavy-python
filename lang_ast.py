"""This module publicly re-exports the types defined dynamically by ast_impl,
hiding the metaprogramming that goes on inside.
"""

import ast_impl
import sys

# Reexport the public types
globals().update({
    # statics
    'AstNode': ast_impl.AstNode,
    'Expression': ast_impl.Expression,
    'Statement': ast_impl.Statement,
    # the dynamically-generated Visitor ABC
    'ExprVisitor': ast_impl.ExprVisitor,
    'StmtVisitor': ast_impl.StmtVisitor,
    # the dynamically-generated node types
    **{name: getattr(ast_impl, name)
       for name in {**ast_impl.EXPR_NODES, **ast_impl.STMT_NODES}},
})

# the inner module is to be regarded as an implementation detail, and hidden
# from the public module. This is somewhat unusual and discouraged by Python's
# culture, but I want to not expose the magic as much as possible. The
# justification is that I'd like to be able to fearlessly `from lang_ast import
# *` and know that I only get language items.
del sys.modules['ast_impl']
del ast_impl
