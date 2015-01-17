"""

    meuh.builder.bot
    ~~~~~~~~~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Bot', 'BotSettings']

import logging
import os
from meuh import distro  # TODO should be late loaded
from meuh.conf import settings
from meuh.hub import connect, AlreadyExists
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
        self.settings = BotSettings(name)

    @classmethod
    def initialise(cls, name):
        client = connect()

        try:
            instance = cls.get_by_name(name)
            logger.info('container %s already exists', instance.container_id)
        except NotFound:
            # create a new container

            data = BotSettings(name)

            try:
                distro.create(data['distro'])
            except AlreadyExists:
                logger.info('distro %s exists', data['distro'])

            image = 'meuh/distro:%s' % data['distro']
            logger.info('create container %s', image)
            container_id = client.create_container(image=image,
                                                   command=['/bin/bash'],
                                                   name=name,
                                                   hostname=name,
                                                   detach=True,
                                                   tty=True,
                                                   stdin_open=True,
                                                   volumes=['/meuh'])
            logger.info('created container %s', container_id)
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
        raise NotFound('builder %s was not found' % name)

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


class BotSettings(object):

    def __init__(self, bot):
        """
        :param bot: a Bot instance or a bot name
        """

        self.bot = bot
        self.data = None

    def __getitem__(self, name):
        if self.data is None:
            self.load()
        return self.data[name]

    def load(self):
        results = {}

        name = getattr(self.bot, 'name', self.bot)

        section = 'builder'
        if settings.has_section(section):
            for key, value in settings.items(section):
                results[key] = value
        else:
            logger.warn('%s is not defined' % section)

        section = 'builder:%s' % name
        if settings.has_section(section):
            for key, value in settings.items(section):
                results[key] = value
        else:
            logger.warn('%s is not defined' % section)

        if 'prereqs' in results:
            results['prereqs'] = [
                cmd for cmd in results['prereqs'].split('\n') if cmd
            ]
        else:
            results['prereqs'] = []

        if 'build-commands' in results:
            results['build-commands'] = [
                cmd for cmd in results['build-commands'].split('\n') if cmd
            ]

        if 'share-dir' not in results:
            directory = os.path.join(settings.get('common', 'share-dir'),
                                     name)
            results['share-dir'] = os.path.expanduser(directory)

        if 'publish-dir' not in results:
            directory = os.path.join(settings.get('common', 'publish-dir'),
                                     name)
            results['publish-dir'] = os.path.expanduser(directory)
        self.data = results


class NotFound(Exception):
    """Raised when does not exists"""
    pass
