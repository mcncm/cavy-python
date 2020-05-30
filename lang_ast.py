"""This module publicly re-exports the types defined dynamically by ast_impl,
hiding the metaprogramming that goes on inside.
"""

import ast_impl
import sys

# the inner module is to be regarded as an implementation detail, and hidden
# from the public module.
sys.modules['ast_impl'] = None

# Reexport the public o
globals().update({
    # statics
    'AstNode': ast_impl.AstNode,
    'Expression': ast_impl.Expression,
    # the dynamically-generated Visitor ABC
    'Visitor': ast_impl.Visitor,
    # the dynamically-generated node types
    **{name: getattr(ast_impl, name) for name in ast_impl.EXPR_NODES}
})
