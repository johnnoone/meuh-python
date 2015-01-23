"""

    meuh.bot
    ~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Bot']

import logging
import os
from meuh.conf import settings
from meuh.api import connect
from meuh.util import copy_dir, ensure_dir

logger = logging.getLogger(__name__)


class Bot(object):
    """Defines a build bot.

    :var name: the bot name
    :var container_id: the docker container id
    """

    name = None
    container_id = None

    def __init__(self, name, container_id=None):
        self.name = name
        self.container_id = container_id

    @property
    def settings(self):
        return settings.bots[self.name]

    @classmethod
    def initialize(cls, name):
        client = connect()

        try:
            instance = cls.get_by_name(name)
            logger.info('running %s for %s', instance.container_id, name)
        except NotFound:
            data = settings.bots[name]
            image = 'meuh/distro:%s' % data['distro']
            container_id = client.create_container(image=image,
                                                   command=['/bin/bash'],
                                                   name=name,
                                                   hostname=name,
                                                   detach=True,
                                                   tty=True,
                                                   stdin_open=True,
                                                   volumes=['/meuh'])
            logger.info('created %s from %s for %s', container_id, image, name)
            instance = cls(name, container_id=container_id)
        instance.start()
        return instance

    @classmethod
    def get_by_name(cls, name):
        client = connect()
        container_name = '/%s' % name
        for container in client.containers(all=True):
            if container_name in container['Names']:
                return cls(name, container_id=container['Id'])
        raise NotFound('bot %s was not found' % name)

    def start(self):
        client = connect()

        inspect = client.inspect_container(self.container_id)
        if not inspect['State']['Running']:
            if not ensure_dir(self.settings['share-dir']):
                logger.info("bind %s:/meuh:rw", self.settings['share-dir'])
            client.start(self.container_id,
                         binds={
                             self.settings['share-dir']: '/meuh',
                         })
            logger.info('start %s', self.container_id)

            for cmd in self.settings['prereqs']:
                res = client.execute(self.container_id, cmd)
                logger.info('EXEC %s', cmd)
                logger.info('RES %s', res)
            return True
        return False

    def publish(self):
        """publish artefacts to host"""
        src = self.settings['share-dir']
        dest = self.settings['publish-dir']

        ensure_dir(dest)
        for suffix in ['*.deb', '*.dsc', '*.tar.gz', '*.changes']:
            filename = os.path.join(src, suffix)
            copy_dir(filename, dest, keep=True)
        logger.info('artifacts are publishes into %s', dest)

    @property
    def arch(self):
        """architecture of the inner distro"""
        client = connect()
        resp = client.execute(self.container_id,
                              'dpkg-architecture -qDEB_HOST_ARCH')
        return resp.strip() or None

    def execute(self, cmd):
        """execute a command into the bot"""
        client = connect()
        formatted = ['/bin/sh', '-c', cmd]
        logger.info('CMD %s', cmd)
        for res in client.execute(self.container_id, cmd=formatted, stream=True):
            logger.info('RES %s', res)

    def kill(self, force=False):
        """Kill the bot"""
        client = connect()
        client.stop(self.container_id)
        client.remove_container(self.container_id, v=True, force=force)
        self.container_id = None

    def build(self, src):
        client = connect()
        src_dir = os.path.join('/meuh', src)
        for cmd in self.settings['build-commands']:
            formatted = ['/bin/sh', '-c', 'cd %s && %s' % (src_dir, cmd)]
            logger.info('CMD %s', cmd)
            for res in client.execute(self.container_id, cmd=formatted, stream=True):
                logger.info('RES %s', res)

    def share(self, host_dir, dest):
        """Expose files into the bot"""
        dest = os.path.join(self.settings['share-dir'], dest)

        return copy_dir(host_dir, dest, keep=False)


class NotFound(Exception):
    """Raised when does not exists"""
    pass
