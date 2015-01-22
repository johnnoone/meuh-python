"""
    meuh.distro
    ~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Distro', 'load_settings']

import json
import logging
import os.path
from meuh.conf import settings, shared
from meuh.api import connect
from six import StringIO
from tempfile import SpooledTemporaryFile

logger = logging.getLogger(__name__)


class Distro(object):
    def __init__(self, name, image_id=None):
        self.name = name
        self.image_id = image_id
        self.settings = load_settings(self)

    @property
    def tag(self):
        return self.settings['tag']

    @property
    def dockerfile(self):
        return as_dockerfile(self.settings)

    @classmethod
    def initialize(cls, name, force=False):
        data = load_settings(name)

        client = connect()
        for image in client.images():
            if data['tag'] in image['RepoTags']:
                if force:
                    client.remove_image(image=image['Id'], force=True)
                else:
                    image_id = image['Id']
                    logger.info('image %s exists', image['Id'])
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
                        raise Exception(response["error"])
                    # {"status":"Downloading","progressDetail":{"current":14050508,"total":90040320,"start":1421605705},"progress":"[=======\u003e                                           ] 14.05 MB/90.04 MB 2m47s","id":"d0a18d3b84de"}

                except:
                    logger.info(line)
        for image in client.images():
            if data['tag'] in image['RepoTags']:
                return cls(name, image['Id'])
        raise Exception('Unexpected error')


def load_settings(distro):
    results, envs = {}, {}

    name = getattr(distro, 'name', distro)

    section = 'distro'
    if settings.has_section(section):
        for key, value in settings.items(section):
            results[key] = value
    else:
        logger.warn('%s is not defined' % section)

    section = 'distro:%s' % name
    if settings.has_section(section):
        for key, value in settings.items(section):
            results[key] = value
    else:
        logger.warn('%s is not defined' % section)

    section = 'env'
    if settings.has_section(section):
        for key, value in settings.items(section):
            envs[key] = value
    else:
        logger.warn('%s is not defined' % section)

    section = 'env:%s' % name
    if settings.has_section(section):
        for key, value in settings.items(section):
            envs[key] = value
    else:
        logger.warn('%s is not defined' % section)

    if 'tag' not in results:
        results['tag'] = 'meuh/distro:%s' % name

    results['envs'] = envs

    return results


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
            yield '%s=%s' % (k, v)

    buffer = StringIO()
    buffer.write('FROM meuh/distro:%s\n' % data['distro'])
    buffer.write('MAINTAINER Cowgirl MEUH cowgirl@iscool-e.com\n')
    buffer.write('ENV %s\n' % ' '.join(kv(data['envs'])))

    if 'prereqs' in data:
        commands = [cmd for cmd in data['prereqs'].split('\n') if cmd]
        for cmd in commands:
            buffer.write('RUN %s\n' % cmd)
    return buffer.getvalue()
