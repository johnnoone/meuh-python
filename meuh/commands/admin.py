"""
    meuh.commands.admin
    ~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['SettingsCommand']

import json
import logging
from meuh.action import bot_destroy, distro_destroy
from meuh.conf import settings
from meuh.exceptions import NotFound
from cliff.command import Command


class SettingsCommand(Command):
    'display configuration'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SettingsCommand, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        print(json.dumps(settings.cached, indent=4))


class DestroyAllCommand(Command):
    'destroy bots and distro'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DestroyAllCommand, self).get_parser(prog_name)
        parser.add_argument('--keep-bots', action='store_true')
        parser.add_argument('--keep-distros', action='store_true')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.keep_bots:
            for name in settings.bots.keys():
                try:
                    bot_destroy(name, parsed_args.force)
                    self.log.info('%s has been destroyed' % name)
                except NotFound:
                    pass
                except Exception as e:
                    self.log.error(e)

        if not parsed_args.keep_distros:
            for name in settings.distros.keys():
                try:
                    distro_destroy(name, parsed_args.force)
                    self.log.info('%s has been destroyed' % name)
                except NotFound:
                    pass
                except Exception as e:
                    self.log.error(e)
