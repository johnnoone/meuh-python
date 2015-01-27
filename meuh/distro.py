"""
    meuh.distro
    ~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Distro']

import json
import logging
import os.path
from meuh import ctx
from meuh.api import connect
from meuh.conf import settings
from meuh.exceptions import NotFound
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

    def destroy(self, force=False):
        client = connect()
        client.remove_image(self.image_id, force)
        logger.info('destroyed %s for %s', self.image_id, self.name)
        self.image_id = None

    @classmethod
    def get_by_name(cls, name):
        data = settings.distros[name]
        client = connect()

        client = connect()
        for image in client.images():
            if data['tag'] in image['RepoTags']:
                logger.info('running %s for %s', image['Id'], name)
                return cls(name, image['Id'])
        raise NotFound('distro %s does not exists' % name)

    @classmethod
    def initialize(cls, name, force=False):
        data = settings.distros[name]

        client = connect()
        try:
            instance = cls.get_by_name(name)
            if not force:
                logger.info('running %s for %s', instance.image_id, instance.name)
                return instance
            client.remove_image(instance.image_id, force=True)
        except NotFound:
            pass

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

                except:
                    logger.info(line)
        for image in client.images():
            if data['tag'] in image['RepoTags']:
                logger.info('created %s for %s', image['Id'], name)
                return cls(name, image['Id'])
        raise RuntimeError('failed to create %s' % name)


def as_dockerfile(data):
    buffer = StringIO()
    if 'docker-file' in data:
        filename = data['docker-file']
        if not os.path.exists(filename):
            raise ValueError('file %s does not exists' % filename)

        with open(filename) as file:
            for line in file:
                buffer.write(line)
    elif 'distro' in data:
        buffer.write('FROM meuh/distro:%s\n' % data['distro'])
        buffer.write('MAINTAINER Cowgirl MEUH cowgirl@iscool-e.com\n')
    else:
        raise RuntimeError('docker-file or distro are mandatories')

    if data['env']:
        env = ctx.inline(data['env'])
        buffer.write('ENV %s\n' % env)

    for cmd in data['prereqs']:
        buffer.write('RUN %s\n' % cmd)
    print(buffer.getvalue())
    return buffer.getvalue()
