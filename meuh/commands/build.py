"""
    meuh.commands.build
    ~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['BuildCommand', 'PublishCommand']

import logging
import os
from meuh.action import build_src, build_publish, bot_settings, distro_init, bot_init, fetch_src  # noqa
from meuh.ctx import EnvBuilder
from meuh.deb import Source
from cliff.command import Command


class BuildCommand(Command):
    'build packages'

    log = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(BuildCommand, self).__init__(*args, **kwargs)
        self.env_builder = EnvBuilder()

    def get_parser(self, prog_name):
        parser = super(BuildCommand, self).get_parser(prog_name)
        parser.add_argument('bot', help='name of the bot to build')
        parser.add_argument('--path', help='path to the source directory')

        self.env_builder.set_arguments(parser)

        return parser

    def take_action(self, parsed_args):
        src_dir = parsed_args.path or os.getcwd()
        src = Source(src_dir)
        env = self.env_builder.parse(parsed_args)

        data = bot_settings(parsed_args.bot)
        distro_init(data['distro'], False)
        bot_init(parsed_args.bot)
        build_src(parsed_args.bot, src.name, src_dir, env)


class FetchCommand(Command):
    'fetch sources from bot'

    log = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(FetchCommand, self).__init__(*args, **kwargs)
        self.env_builder = EnvBuilder()

    def get_parser(self, prog_name):
        parser = super(FetchCommand, self).get_parser(prog_name)
        parser.add_argument('bot', help='name of the bot')
        parser.add_argument('pkg', help='name of the package to source')
        parser.add_argument('--path', help='path to the source directory')

        return parser

    def take_action(self, parsed_args):
        src_dir = parsed_args.path or os.getcwd()
        fetch_src(parsed_args.bot, parsed_args.pkg, src_dir)


class PublishCommand(Command):
    'publish builts'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PublishCommand, self).get_parser(prog_name)
        parser.add_argument('bot', help='name of the bot to build')
        return parser

    def take_action(self, parsed_args):
        build_publish(parsed_args.bot)
