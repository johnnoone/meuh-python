"""
    meuh.deb.source_control
    ~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

from .util import iter_src


class SourceControl(object):
    @classmethod
    def parse(self, obj):
        raise NotImplementedError()


def load(obj):
    response = {}
    for line in iter_src(obj):
        if line == '-----BEGIN PGP SIGNED MESSAGE-----':
            continue

        if line == '-----BEGIN PGP SIGNATURE-----':
            break
    return response
