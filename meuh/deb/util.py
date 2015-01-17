"""
    meuh.deb.util
    ~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['iter_src', 'parse_version']

from six import StringIO


def iter_src(obj):
    """Obj must be a str or file handler file
    """
    try:
        for line in obj.readlines():
            yield line.rstrip('\n')
    except AttributeError:
        # not a file object?
        for line in StringIO(obj).readlines():
            yield line.rstrip('\n')


def parse_version(version):
    # https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version

    epoch, _, remains = version.rpartition(':')
    upstream, _, rev = version.partition('-')
    return {
        'epoch': epoch or None,
        'upstream': upstream or None,
        'debian_revision': rev or None
    }
