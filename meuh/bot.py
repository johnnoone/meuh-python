"""
    meuh.bot
    ~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Bot']

import logging
import os.path
from meuh import ctx
from meuh import host
from meuh.api import connect
from meuh.conf import settings
from meuh.exceptions import NotFound
from meuh.util import copy_dir, ensure_dir
from tarfile import TarFile
from tempfile import SpooledTemporaryFile

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

            # mmmhhhh.
            from meuh.distro import Distro
            distro = Distro.initialize(data['distro'], force=False)

            container_id = client.create_container(image=distro.tag,
                                                   command=['/bin/bash'],
                                                   name=name,
                                                   hostname=name,
                                                   detach=True,
                                                   tty=True,
                                                   stdin_open=True,
                                                   volumes=[
                                                       '/meuh/build',
                                                       '/meuh/publish'
                                                   ])
            logger.info('created %s from %s for %s',
                        container_id,
                        distro.tag,
                        name)
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
            if not ensure_dir(self.settings['build-dir']):
                logger.info("bind %s:/meuh:rw", self.settings['build-dir'])
            if not ensure_dir(self.settings['publish-dir']):
                logger.info("bind %s:/meuh:rw", self.settings['publish-dir'])
            client.start(self.container_id,
                         binds={
                             self.settings['build-dir']: '/meuh/build',
                             self.settings['publish-dir']: '/meuh/publish',
                         })
            logger.info('start %s', self.container_id)

            for cmd in self.settings['prereqs']:
                res = client.execute(self.container_id, cmd)
                logger.info('EXEC %s', cmd)
                logger.info('RES %s', res)
            return True
        return False

    def publish(self):
        """publish artefacts"""
        client = connect()

        patterns = ['*.deb', '*.dsc', '*.tar.gz', '*.tar.xz', '*.changes']
        batch = []
        for pattern in patterns:
            batch.append('cp -r /meuh/build/%s /meuh/publish' % pattern)
        cmd = ['/bin/sh', '-c', '; '.join(batch)]
        for res in client.execute(self.container_id, cmd=cmd, stream=True):
            logger.info('RES %s', res)
        logger.info('artifacts are published into /meuh/publish')

    @property
    def arch(self):
        """architecture of the inner distro"""
        client = connect()
        resp = client.execute(self.container_id,
                              'dpkg-architecture -qDEB_HOST_ARCH')
        return resp.strip() or None

    def execute(self, cmd):
        """Execute a command into the bot"""
        client = connect()
        formatted = ['/bin/sh', '-c', cmd]
        logger.info('execute %s', cmd)
        for res in client.execute(self.container_id,
                                  cmd=formatted,
                                  stream=True):
            print(res, end='')

    def _exec(self, cmd):
        client = connect()
        formatted = ['/bin/sh', '-c', cmd]
        for res in client.execute(self.container_id,
                                  cmd=formatted,
                                  stream=True,
                                  stdout=True,
                                  stderr=True):
            print(res, end='')

    def destroy(self, force=False):
        """Destroy the bot"""
        client = connect()
        client.stop(self.container_id)
        client.remove_container(self.container_id, v=True, force=force)
        logger.info('destroyed %s for %s', self.container_id, self.name)
        self.container_id = None

    def build(self, src_name, src_dir, env=None):
        # copy files into shared volume
        shared_dir = os.path.join(self.settings['build-dir'], src_name)
        host.execute('mkdir -p %s' % shared_dir)
        src_dir = os.path.abspath(src_dir)
        parent_dir, src = os.path.dirname(src_dir), os.path.basename(src_dir)
        args = [
            "rsync --delete-excluded --recursive",
            "--include='%s'" % src,
            "--include='%s/*'" % src,
            "--include='%s/**/*'" % src,
            "--include='%s_*.orig.*'" % src_name,
            "--include='%s.orig.*'" % src_name,
            "--exclude='*'",
            "%s/" % parent_dir,
            "%s/" % shared_dir,
        ]
        host.execute(' '.join(args))

        # build packages

        client = connect()

        work_dir = os.path.join('/meuh/build', src_name, src)
        env = ctx.inline(env or {})

        for cmd in self.settings['publish-commands']:
            formatted = ['/bin/sh', '-c', '%s' % cmd]
            logger.info('execute %s', cmd)
            for res in client.execute(self.container_id,
                                      cmd=formatted,
                                      stream=True):
                print(res, end='')

        for cmd in self.settings['build-commands']:
            formatted = ['/bin/sh',
                         '-c',
                         'cd %s && %s %s' % (work_dir, env, cmd)]
            logger.info('execute %s', 'cd %s && %s %s' % (work_dir, env, cmd))
            for res in client.execute(self.container_id,
                                      cmd=formatted,
                                      stream=True):
                print(res, end='')

        # publish results
        args = [
            "rsync --recursive",
            "--include='*.deb'",
            "--include='*.udeb'",
            "--include='*.dsc'",
            "--include='*.changes'",
            "--exclude='*'",
            "%s/" % os.path.join('/meuh/build', src_name),
            '/meuh/publish'
        ]
        self.execute(' '.join(args))
        logger.info('artifacts are published into /meuh/publish')

    def build2(self, src, env=None):
        client = connect()
        src_dir = os.path.join('/meuh/build', src)
        env = ctx.inline(env or {})

        for cmd in self.settings['publish-commands']:
            formatted = ['/bin/sh', '-c', '%s' % cmd]
            logger.info('execute %s', cmd)
            for res in client.execute(self.container_id,
                                      cmd=formatted,
                                      stream=True):
                print(res, end='')

        for cmd in self.settings['build-commands']:
            formatted = ['/bin/sh',
                         '-c',
                         'cd %s && %s %s' % (src_dir, env, cmd)]
            logger.info('execute %s', 'cd %s && %s %s' % (src_dir, env, cmd))
            for res in client.execute(self.container_id,
                                      cmd=formatted,
                                      stream=True):
                print(res, end='')

    def cleanup(self, dest):
        """Cleanup bot files"""
        dest = os.path.join('/meuh/build', dest)
        cmd = ['rm', '-rf', dest]
        client = connect()
        logger.info('execute %s', cmd)
        for res in client.execute(self.container_id, cmd=cmd, stream=True):
            print(res)

    def share(self, host_dir, dest):
        """Expose files into the bot"""
        dest = os.path.join(self.settings['build-dir'], dest)

        return copy_dir(host_dir, dest, keep=False)

    def fetch_src(self, pkg, parent_dir):
        """Fetch sources of package"""

        work_dir = '/tmp/meuh/%s' % pkg
        self.execute('mkdir -p %s' % work_dir)
        self.execute('rm -rf %s/*' % work_dir)
        self.execute('cd %s && apt-get update && apt-get source %s' % (work_dir, pkg))  # noqa

        tmp_dir = host.execute('mktemp -d /tmp/meuh-src.XXXX').stdout.strip()
        self.download(work_dir, tmp_dir, extract_here=True)
        host.execute('mkdir -p %s' % parent_dir)
        host.execute('rsync --delete-after --recursive %s/* %s/' % (tmp_dir, parent_dir))  # noqa
        host.execute('rm -rf %s' % tmp_dir)
        self.execute('rm -rf %s/*' % work_dir)

    def download(self, src, dest, extract_here=False):
        client = connect()

        with SpooledTemporaryFile() as file:
            file.write(client.copy(self.container_id, src).read())
            file.seek(0)
            tfile = TarFile(fileobj=file)
            if extract_here:
                base = len(os.path.basename(src)) + 1
                for member in tfile.getmembers():
                    member.name = member.name[base:]
            tfile.extractall(path=dest)
