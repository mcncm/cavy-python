"""Global data about the system: locations of helper files and so on.
"""

import os

# A temporary project codename!
LANG_NAME = 'Cavy'

PROJ_DIR = os.path.dirname(__file__)
GIT_DIR = os.path.join(PROJ_DIR, '.git')

# This is a directory, not a file, but who says "dot-directory?"
DOTFILE = os.path.join(os.path.expanduser('~'), '.' + LANG_NAME.lower())
# Let's ensure this directory's existence on import, so that it can't be
# referenced without existing.
os.makedirs(DOTFILE, exist_ok=True)

CRASHLOG = os.path.join(DOTFILE, 'crashlog.json')

