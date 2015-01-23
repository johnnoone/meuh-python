"""
    meuh.commands.distro
    ~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['InitCommand',
           'DestroyAllCommand',
           'DestroyCommand',
           'ShowCommand']

import logging
from cliff.command import Command
from meuh.action import distro_dockerfile, distro_init, distributions, distro_destroy
from meuh.conf import settings
from meuh.exceptions import NotFound


class InitCommand(Command):
    'create distribution'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(InitCommand, self).get_parser(prog_name)
        parser.add_argument('distro')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        data = distro_init(parsed_args.distro, parsed_args.force)
        print('created %s %s' % (parsed_args.distro, data))


class ShowCommand(Command):
    'show distribution'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        parser.add_argument('distro')
        return parser

    def take_action(self, parsed_args):
        data = distro_dockerfile(parsed_args.distro)
        print(data)


class ListCommand(Command):
    'list distributions'

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        for name, status in distributions().items():
            print(name, status)


class DestroyCommand(Command):
    'destroy a single distro'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DestroyCommand, self).get_parser(prog_name)
        parser.add_argument('distro')
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        distro_destroy(parsed_args.distro, parsed_args.force)
        self.log.info('%s has been destroyed' % parsed_args.bot)


class DestroyAllCommand(Command):
    'destroy all distros'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DestroyAllCommand, self).get_parser(prog_name)
        parser.add_argument('--force', action='store_true')
        return parser

    def take_action(self, parsed_args):
        for name in settings.distros.keys():
            try:
                distro_destroy(name, parsed_args.force)
                self.log.info('%s has been destroyed' % name)
            except NotFound:
                pass
            except Exception as e:
                self.log.error(e)
