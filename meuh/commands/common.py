"""
    meuh.commands.common
    ~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['SettingsCommand']

import json
import logging
from meuh.conf import settings
from cliff.command import Command


class SettingsCommand(Command):
    'display configuration'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SettingsCommand, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        c = settings.cached
        print(json.dumps(c, indent=4))
