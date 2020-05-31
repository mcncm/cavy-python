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
    # the dynamically-generated Visitor ABC
    'Visitor': ast_impl.Visitor,
    # the dynamically-generated node types
    **{name: getattr(ast_impl, name) for name in ast_impl.EXPR_NODES}
})

# the inner module is to be regarded as an implementation detail, and hidden
# from the public module. This is somewhat unusual and discouraged by Python's
# culture, but I want to not expose the magic as much as possible.
del sys.modules['ast_impl']
del ast_impl
