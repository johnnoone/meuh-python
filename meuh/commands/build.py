"""
    meuh.commands.build
    ~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['BuildCommand', 'PublishCommand']

import logging
import os
from meuh.action import build_src, build_publish, bot_settings, distro_init, bot_init
from meuh.deb import Source
from cliff.command import Command


class BuildCommand(Command):
    'build packages'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(BuildCommand, self).get_parser(prog_name)
        parser.add_argument('bot', help='name of the bot to build')
        parser.add_argument('--path', help='path to the source directory')
        return parser

    def take_action(self, parsed_args):
        src_dir = parsed_args.path or os.getcwd()
        src = Source(src_dir)

        data = bot_settings(parsed_args.bot)
        distro_init(data['distro'], False)
        bot_init(parsed_args.bot)
        build_src(parsed_args.bot, src.name, src_dir)


class PublishCommand(Command):
    'publish builts'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PublishCommand, self).get_parser(prog_name)
        parser.add_argument('bot', help='name of the bot to build')
        return parser

    def take_action(self, parsed_args):
        build_publish(parsed_args.bot)
