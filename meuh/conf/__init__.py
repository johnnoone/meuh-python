"""

    meuh.conf
    ~~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['ini', 'settings']

import os.path
import tempfile
from six.moves.configparser import ConfigParser
from .loader import Loader

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'share')
DEFAULT_FILE = os.path.join(DATA_DIR, 'defaults.cfg')

ini = ConfigParser()
ini.optionxform = str  # avoid .lower() method
ini.add_section('common')
ini.set('common', 'share-dir', os.path.join(tempfile.gettempdir(), 'meuh'))

with open(DEFAULT_FILE) as file:
    ini.readfp(file)
ini.read(['/etc/meuh.cfg', os.path.expanduser('~/.meuh.cfg'), '.meuh.cfg'])


def shared(filename):
    return os.path.join(DATA_DIR, filename)


class Settings(object):
    def __init__(self, ini, data_dir):
        self.ini = ini
        self.loader = Loader(data_dir)
        self.fresh = False

    def read(self, filename):
        self.ini.read(filename)
        self.fresh = False

    def __getitem__(self, name):
        return self.cached[name]

    @property
    def docker(self):
        return self.cached['docker']

    @property
    def distros(self):
        return self.cached['distros']

    @property
    def bots(self):
        return self.cached['bots']

    @property
    def cached(self):
        if not self.fresh:
            self._cached = self.loader(self.ini)
            self.fresh = True
        return self._cached

settings = Settings(ini, DATA_DIR)
