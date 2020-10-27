"""
This __init__ file is used when we import cavy-python as a package
to make its resources available in a convenient way to the user.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from compilation import Program
import circuits.backends as backends
