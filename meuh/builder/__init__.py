"""
    meuh.builder
    ~~~~~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['bot_build', 'bot_init', 'bot_settings', 'bot_stop', 'Bot']

import os.path
from .bot import Bot


def bot_init(name, force=False):
    Bot.initialise(name)


def bot_settings(name):
    return Bot(name).settings


def bot_stop(name, force=False):
    Bot.get_by_name(name).kill(force)


def bot_build(name, src_name, src_dir):
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

    bot = Bot.initialise(name)
    bot.share(os.path.join(src_dir, '.'),
              os.path.join(src_base, '.'))
    bot.share(os.path.join(src_dir, orig),
              os.path.join(src_base, '..'))
    bot.build(src_base)
    bot.publish()
