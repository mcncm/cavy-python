"""This module is included to allow lazy-loading of dependencies that may be
required for individual functions, which may be (for example) backend-dependent.
"""

import importlib
from functools import wraps
from typing import Callable, Any, List

from errors import CavyRuntimeError

DEPENDENCIES = {
    'cirq',
}

LOADED_DEPENDENCIES = set()


class MissingDependencyError(CavyRuntimeError):
    def __init__(self, dep):
        assert dep in DEPENDENCIES
        self.dep = dep

    def __str__(self):
        return f"Error: this feature requires the missing dependency '{dep}'."


def load_dependency(dep):
    try:
        globals()[dep] = importlib.import_module(dep)
        LOADED_DEPENDENCIES.add(dep)
    except ModuleNotFoundError as e:
        raise e


def require(*deps: List[str]) -> Callable:
    """Annotation for a function that requires a dependency.
    This dependency is lazy-loaded the first time it's used.
    """
    def require_dep(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args, **kwargs) -> Any:
            for dep in deps:
                if dep not in LOADED_DEPENDENCIES:
                    try:
                        load_dependency(dep)
                    except ModuleNotFoundError as e:
                        raise MissingDependencyError(dep)
            return fn(*args, **kwargs)
        return wrapped
    return require_dep
