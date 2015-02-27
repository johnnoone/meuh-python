"""
    meuh.api
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

logger = logging.getLogger(__name__)


def connect():
    """connect to docker"""
    if connect.client:
        return connect.client

    if is_tool('boot2docker'):
        params = kwargs_from_env()
        params['tls'].assert_hostname = False
    else:
        params = {
            'base_url': settings.docker['base-url']
        }

    connect.client = Client(**params)
    return connect.client
connect.client = None


def is_tool(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True


def is_running(name):
    from meuh import host
    resp = host.execute("ps aux | grep '\--comment boot2docker-vm'").returncode
    return resp == 0
