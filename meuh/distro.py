"""
    meuh.distro
    ~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Distro']

import json
import logging
import os.path
from meuh.conf import shared, settings
from meuh.api import connect
from six import StringIO
from tempfile import SpooledTemporaryFile

logger = logging.getLogger(__name__)


class Distro(object):
    def __init__(self, name, image_id=None):
        self.name = name
        self.image_id = image_id

    @property
    def settings(self):
        return settings.distros[self.name]

    @property
    def tag(self):
        return self.settings['tag']

    @property
    def dockerfile(self):
        return as_dockerfile(self.settings)

    @classmethod
    def initialize(cls, name, force=False):
        data = settings.distros[name]

        client = connect()
        for image in client.images():
            if data['tag'] in image['RepoTags']:
                if force:
                    client.remove_image(image=image['Id'], force=True)
                    logger.info('removed %s for %s', image['Id'], name)
                else:
                    image_id = image['Id']
                    logger.info('running %s for %s', image['Id'], name)
                    return cls(name, image_id)

        dockerfile = as_dockerfile(data)
        with SpooledTemporaryFile() as file:
            file.write(dockerfile.encode('utf-8'))
            file.seek(0)
            for line in client.build(fileobj=file,
                                     forcerm=True,
                                     rm=True,
                                     tag=data['tag'],
                                     nocache=True):
                try:
                    response = json.loads(line)
                    if 'stream' in response:
                        logger.info(response['stream'])
                    if 'error' in response:
                        logger.error(response['error'])
                    # {"status":"Downloading","progressDetail":{"current":14050508,"total":90040320,"start":1421605705},"progress":"[=======\u003e                                           ] 14.05 MB/90.04 MB 2m47s","id":"d0a18d3b84de"}

                except:
                    logger.info(line)
        for image in client.images():
            if data['tag'] in image['RepoTags']:
                logger.info('created %s for %s', image['Id'], name)
                return cls(name, image['Id'])
        raise RuntimeError('failed to create %s' % name)


def as_dockerfile(data):
    if 'docker-file' in data:
        basename = data['docker-file']
        for filename in [os.path.expanduser(basename), shared(basename)]:
            if os.path.exists(filename):
                break
        else:
            raise ValueError('file %s does not exists' % basename)

        with open(filename) as file:
            return file.read()
    elif 'distro' not in data:
        raise Exception('docker-file or distro are mandatories')

    def kv(data):
        for k, v in data.items():
            yield '%s=%r' % (k, v)

    buffer = StringIO()
    buffer.write('FROM meuh/distro:%s\n' % data['distro'])
    buffer.write('MAINTAINER Cowgirl MEUH cowgirl@iscool-e.com\n')
    buffer.write('ENV %s\n' % ' '.join(kv(data['env'])))

    for cmd in data['prereqs']:
        buffer.write('RUN %s\n' % cmd)
    return buffer.getvalue()
