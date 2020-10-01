"""Global data about the system: locations of helper files and so on.
"""

import os

LANG_NAME = 'Cavy'
LANG_SEMVER = "0.1.0"

# Mild obfuscation to evade scrapers
HELP_ADDRESS = '{}-{}-{}'.format(LANG_NAME.lower(), 'lang', 'support') + \
    chr(0x3F + 1) + 'mit' + chr(46) + 'e' "d" """u"""
REPO_URL = 'h' + 't' * 2 + 'ps:' + '/' * 2 + 'git' 'hub' + chr(46) +\
    'com' + chr(0x2F) + '{}n{}'.format('mc', 'cm') + '/' +\
    'cavy-python'

PROJ_DIR = os.path.dirname(__file__)
GIT_DIR = os.path.join(PROJ_DIR, '.git')

# This is a directory, not a file, but who says "dot-directory?"
DOTFILE = os.path.join(os.path.expanduser('~'), '.' + LANG_NAME.lower())
# Let's ensure this directory's existence on import, so that it can't be
# referenced without existing.
os.makedirs(DOTFILE, exist_ok=True)

CRASHLOG = os.path.join(DOTFILE, 'crashlog.json')

