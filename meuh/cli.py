"""
    meuh.cli
    ~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['main', 'MeuhApp']

import logging
import meuh
import os.path
import sys
from cliff.app import App
from cliff.commandmanager import CommandManager
from meuh.conf import settings


class MeuhApp(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        super(MeuhApp, self).__init__(
            description='meuh demo app',
            version=meuh.__version__,
            command_manager=CommandManager('meuh.commands'),
        )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(MeuhApp, self).build_option_parser(description,
                                                          version,
                                                          argparse_kwargs)
        parser.add_argument('--config', help="additional config file")
        return parser

    def initialize_app(self, argv):
        configfile = self.options.config
        if configfile:
            self.log.debug('load configuration %s', configfile)
            settings.read([os.path.expanduser(configfile)])

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = MeuhApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
