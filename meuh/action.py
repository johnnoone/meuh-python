"""
    meuh.action
    ~~~~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['build_src', 'build_publish',
           'bot_init', 'bot_settings', 'bot_stop', 'Bot']

import os.path
from collections import defaultdict

from meuh.bot import Bot
from meuh.conf import settings
from meuh.api import connect
from meuh.distro import Distro


def bot_init(name, force=False):
    Bot.initialize(name)


def bot_settings(name):
    return Bot(name).settings


def bot_stop(name, force=False):
    Bot.get_by_name(name).kill(force)


def build_src(name, src_name, src_dir):
    """Build a package.

    Steps:

    - init builder if it not exists yet
    - copy current package into builder share
    - do we have a orig file ?
    - build the package
    - publish results
    """

    src_base = os.path.basename(src_dir)
    orig = '../%s_*.orig.tar.gz' % src_name

    bot = Bot.initialize(name)
    bot.share(os.path.join(src_dir, '.'),
              os.path.join(src_base, '.'))
    bot.share(os.path.join(src_dir, orig),
              os.path.join(src_base, '..'))
    bot.build(src_base)
    bot.publish()


def build_publish(name):
    """Publish builts.
    """

    bot = Bot.initialize(name)
    bot.publish()


def distro_init(name, force=False):
    Distro.initialize(name, force)


def distributions():
    distributions = defaultdict(lambda: {
        'defined': False,
        'created': False,
    })
    client = connect()

    for name in settings.distros.keys():
        distributions[name]['defined'] = True

    for data in client.images():
        for tag in data['RepoTags']:
            if tag.startswith('meuh/distro:'):
                distributions[tag[12:]]['created'] = True
    return distributions


def distro_dockerfile(name):
    return Distro(name).dockerfile


def distro_settings(name):
    return Distro(name).settings
