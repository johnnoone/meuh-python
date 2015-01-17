"""
    meuh.deb.exceptions
    ~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals


class ParseError(ValueError):
    pass


class LoadError(Exception):
    pass
