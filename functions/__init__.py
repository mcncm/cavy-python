from .function import Function
from .lang_builtins import *

BUILTINS = {
    'qubit': AllocQubit(),
    'split': Split(),
    'phase': Phase(),
    'debug': Debug(),
}
