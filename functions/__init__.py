from .function import Function
from .lang_builtins import *

BUILTINS = {
    'qubit': AllocQubit(),
    'not':   Not(),
    'split': Split(),
    'flip':  Flip(),
    'debug': Debug(),
}
