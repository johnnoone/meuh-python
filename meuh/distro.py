"""
    meuh.deb.distro
    ~~~~~~~~~~~~~~~
"""

__all__ = ['create']

import logging
import os.path
from collections import defaultdict
from six import StringIO

from meuh.conf import settings, shared
from meuh.hub import connect, create_from_string

logger = logging.getLogger(__name__)


def create(name, force=None):
    """create image"""
    tag = 'meuh/distro:%s' % name

    logger.info('create %s start', name)
    logger.info('tag will be %s', tag)

    container, envs = load(name)

    buffer = dockerfile(name)
    create_from_string(tag, buffer, force)


def distributions():
    distributions = defaultdict(lambda: {
        'defined': False,
        'created': False,
    })
    client = connect()

    for section in settings.sections():
        if section.startswith('distro:'):
            distributions[section[7:]]['defined'] = True

    for data in client.images():
        for tag in data['RepoTags']:
            if tag.startswith('meuh/distro:'):
                distributions[tag[12:]]['created'] = True
    return distributions


def dockerfile(name):
    container, env = load(name)

    if 'docker-file' in container:
        basename = container['docker-file']
        for filename in [os.path.expanduser(basename), shared(basename)]:
            if os.path.exists(filename):
                break
        else:
            raise ValueError('file %s does not exists' % basename)

        with open(filename) as file:
            return file.read()
    elif 'distro' not in container:
        raise Exception('docker-file or distro are mandatories')

    def kv(data):
        for k, v in data.items():
            yield '%s=%s' % (k, v)

    buffer = StringIO()
    buffer.write('FROM meuh/distro:%s\n' % container['distro'])
    buffer.write('MAINTAINER Cowgirl MEUH cowgirl@iscool-e.com\n')
    buffer.write('ENV %s\n' % ' '.join(kv(env)))

    if 'prereqs' in container:
        commands = [cmd for cmd in container['prereqs'].split('\n') if cmd]
        for cmd in commands:
            buffer.write('RUN %s\n' % cmd)
    return buffer.getvalue()


def load(name):
    """docstring for load"""

    container, envs = {}, {}

    section = 'distro'
    if settings.has_section(section):
        for key, value in settings.items(section):
            container[key] = value
    else:
        logger.warn('%s is not defined' % section)

    section = 'distro:%s' % name
    if settings.has_section(section):
        for key, value in settings.items(section):
            container[key] = value
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

    return container, envs
