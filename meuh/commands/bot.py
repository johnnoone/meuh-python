"""
    meuh.commands.bot
    ~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['InitCommand',
           'ShowCommand',
           'StopCommand']

from cliff.command import Command
from meuh.action import bot_init, bot_settings, bot_stop, distro_init
import logging


class InitCommand(Command):
    'create docker builder'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(InitCommand, self).get_parser(prog_name)
        parser.add_argument('bot')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        data = bot_settings(parsed_args.bot)
        distro_init(data['distro'], False)
        bot_init(parsed_args.bot, parsed_args.force)
        print('created %s' % parsed_args.bot)


class ShowCommand(Command):
    'show docker builder'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        parser.add_argument('bot')
        return parser

    def take_action(self, parsed_args):
        container = bot_settings(parsed_args.bot)
        print(container)


class StopCommand(Command):
    'create docker builder'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StopCommand, self).get_parser(prog_name)
        parser.add_argument('bot')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        bot_stop(parsed_args.bot, parsed_args.force)
        print('stopped %s' % parsed_args.bot)
