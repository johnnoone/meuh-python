"""
    meuh.commands
    ~~~~~~~~~~~~~

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['BuildCommand']

import logging
import os
from meuh.builder import bot_build
from meuh.deb import Source
from cliff.command import Command


class BuildCommand(Command):
    'build package'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(BuildCommand, self).get_parser(prog_name)
        parser.add_argument('builder', help='name of the builder to build')
        parser.add_argument('--path', help='path of the source directory')
        return parser

    def take_action(self, parsed_args):
        src_dir = parsed_args.path or os.getcwd()
        src = Source(src_dir)
        bot_build(parsed_args.builder, src.name, src_dir)
