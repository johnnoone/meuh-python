"""

    meuh.conf
    ~~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['settings']

import os.path
import tempfile
from six.moves.configparser import ConfigParser

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(HERE, 'share', 'defaults.cfg')

settings = ConfigParser()
settings.optionxform = str  # avoid .lower() method
settings.add_section('common')
settings.set('common', 'share-dir', os.path.join(tempfile.gettempdir(), 'meuh'))

with open(DEFAULT_FILE) as file:
    settings.readfp(file)
settings.read(['/etc/meuh.cfg',
               os.path.expanduser('~/.meuh.cfg'),
               '.meuh.cfg'])


def shared(filename):
    return os.path.join(HERE, 'share', filename)
