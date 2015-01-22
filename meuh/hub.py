"""
    meuh.hub
    ~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['connect']

import logging
import subprocess
import os
from docker import Client
from docker.utils import kwargs_from_env
from meuh.conf import settings

# TODO chomp latest \n from meuh.hub handler

logger = logging.getLogger(__name__)


def connect():
    """connect to docker"""

    if is_tool('boot2docker'):
        params = kwargs_from_env()
        params['tls'].assert_hostname = False
    else:
        params = {
            'base_url': settings.get('docker', 'base-url')
        }

    return Client(**params)


def is_tool(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True
