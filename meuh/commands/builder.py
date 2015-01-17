"""
    meuh.commands.builder
    ~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['InitCommand',
           'ShowCommand',
           'StopCommand']

from cliff.command import Command
from meuh.builder import bot_init, bot_settings, bot_stop
import logging


class InitCommand(Command):
    'create docker builder'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(InitCommand, self).get_parser(prog_name)
        parser.add_argument('builder')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        bot_init(parsed_args.builder, parsed_args.force)
        print('created %s' % parsed_args.builder)


class ShowCommand(Command):
    'show docker builder'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        parser.add_argument('builder')
        return parser

    def take_action(self, parsed_args):
        container = bot_settings(parsed_args.builder)
        print(container)


class StopCommand(Command):
    'create docker builder'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StopCommand, self).get_parser(prog_name)
        parser.add_argument('builder')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        bot_stop(parsed_args.builder, parsed_args.force)
        print('stopped %s' % parsed_args.builder)