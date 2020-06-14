import importlib
from functools import wraps
from typing import Callable, Any

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


for dep in DEPENDENCIES:
    try:
        globals()[dep] = importlib.import_module(dep)
        LOADED_DEPENDENCIES.add(dep)
    except ModuleNotFoundError:
        pass


def require(dep: str) -> Callable:
    def require_dep(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args, **kwargs) -> Any:
            if dep not in LOADED_DEPENDENCIES:
                raise MissingDependencyError(dep)
            else:
                return fn(*args, **kwargs)

        return wrapped

    return require_dep
