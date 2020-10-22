"""This module is included to allow lazy-loading of dependencies that may be
required for individual functions, which may be (for example) backend-dependent.
"""

from dataclasses import dataclass
from enum import Enum
import importlib
from functools import wraps
from typing import Callable, Optional, Any, List

from errors import CavyRuntimeError

class DependencyKind(Enum):
    PYTHON_PKG = 'python package'
    UNSATISFIABLE = 'unsatisfiable'

@dataclass
class DependencySpec():
    name: str
    kind: DependencyKind
    url: Optional[str]
    desc: str

# The following specs are all the dependencies used anywhere in the PyCavy system.
DEPENDENCIES = {
    'cirq': DependencySpec(
        name='cirq',
        kind=DependencyKind.PYTHON_PKG,
        url='https://cirq.readthedocs.io/en/stable/',
        desc="""A quantum circuits package"""
    ),
    'pylatex': DependencySpec(
        name='pylatex',
        kind=DependencyKind.PYTHON_PKG,
        url='https://jeltef.github.io/PyLaTeX/current/',
        desc="""A package for drawing LaTeX diagrams for python"""
    ),
    'labber': DependencySpec(
        # The capitalization is intentional!
        name='Labber',
        kind=DependencyKind.PYTHON_PKG,
        url='http://labber.org/online-doc/api/index.html',
        desc="""The Python API for the Labber automation toolkit"""
    ),
    '__unsatisfiable__': DependencySpec(
        name='unsatisfiable',
        kind=DependencyKind.UNSATISFIABLE,
        url=None,
        desc="""A dependency that always fails to load"""
    ),
}

LOADED_DEPENDENCIES = set()

class MissingDependencyError(CavyRuntimeError):
    def __init__(self, dep):
        assert dep in DEPENDENCIES
        self.dep = dep
        self.spec = DEPENDENCIES[dep]

    def __str__(self):
        fmt = """Error: this feature requires the missing dependency '{}'.
Install the '{}' {} [{}]"""
        return fmt.format(self.dep, self.spec.name, self.spec.kind, self.spec.url)


def load_dependency(dep: str):
    try:
        globals()[dep] = importlib.import_module(dep)
        LOADED_DEPENDENCIES.add(dep)
    except ModuleNotFoundError as e:
        raise e


def dependency_version(dep: str) -> str:
    """Try to get the version of a loaded dependency"""
    if dep not in LOADED_DEPENDENCIES:
        return "Not loaded"
    mod = globals()[dep]
    return getattr(mod, '__version__', 'No version found')


def require(*deps: List[str]) -> Callable:
    """Annotation for a function that requires one or more dependencies. These
    dependencies are lazy-loaded on first use.
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
