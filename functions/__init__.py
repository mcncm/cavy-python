from .function import Function
from .lang_builtins import *

BUILTINS = {
    'qubit': AllocQubit(),
    'split': Split(),
    'flip':  Flip(),
    'debug': Debug(),
}
