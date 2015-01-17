"""
    meuh.hub
    ~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['connect', 'create_from_string']

import json
import logging
import subprocess
import os
from docker import Client
from docker.utils import kwargs_from_env
from tempfile import SpooledTemporaryFile
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


def create_from_string(tag, dockerfile, force=False):
    client = connect()
    for image in client.images():
        if tag in image['RepoTags']:
            if force:
                client.remove_image(image=image['Id'], force=True)
            else:
                raise AlreadyExists('%s already exists' % tag)

    with SpooledTemporaryFile() as file:
        file.write(dockerfile.encode('utf-8'))
        file.seek(0)
        for line in client.build(fileobj=file,
                                 forcerm=True,
                                 rm=True,
                                 tag=tag,
                                 nocache=True):
            try:
                data = json.loads(line)
                if 'stream' in data:
                    logger.info(data['stream'])
                if 'error' in data:
                    raise Exception(data["error"])
                # [debian-wheezy] {"status":"Downloading","progressDetail":{"current":14050508,"total":90040320,"start":1421605705},"progress":"[=======\u003e                                           ] 14.05 MB/90.04 MB 2m47s","id":"d0a18d3b84de"}

            except:
                logger.info(line)


class AlreadyExists(Exception):
    """Raised when a container already exists"""
    pass
