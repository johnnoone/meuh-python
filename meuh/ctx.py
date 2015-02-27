"""
    meuh.ctx
    ~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['inline', 'EnvBuilder']

import abc
import logging
from six import add_metaclass
from six.moves import shlex_quote as quote

logger = logging.getLogger(__name__)


@add_metaclass(abc.ABCMeta)
class Param(object):
    pass


class BuildOptionsParam(Param):
    """
    see https://www.debian.org/doc/debian-policy/ch-source.html

    :ivar check: Run build-time test suite provided by the package
    :ivar optimize: Compile package with a maximum of optimization
    :ivar strip: Strip debugging symbols from the binary
    :ivar docs: Built docs
    :ivar parallel: Use n parallel processes to build package
    """

    name = 'DEB_BUILD_OPTIONS'

    safe = True  #: str representation is already quoted

    check = True
    docs = True
    optimize = True
    strip = True
    parallel = 1

    def __init__(self, **opts):
        self.check = opts.pop('check', True)
        self.optimize = opts.pop('optimize', True)
        self.strip = opts.pop('strip', True)
        self.docs = opts.pop('docs', True)
        self.parallel = opts.pop('parallel', 1)
        if opts:
            logger.warn('Unknown options %', opts)

    @classmethod
    def from_env(cls, value):
        attrs = {}
        for flag in value.split():
            if flag == 'nocheck':
                attrs['check'] = False
            elif flag == 'noopt':
                attrs['optimize'] = False
            elif flag == 'nostrip':
                attrs['strip'] = False
            elif flag == 'nodocs':
                attrs['docs'] = False
            elif flag.startswith('parallel='):
                attrs['parallel'] = int(flag[9:])
            else:
                logger.warn('unknow flag %s ', flag)
        return cls(**attrs)

    def __str__(self):
        flags = []
        if not self.check:
            flags.append('nocheck')
        if not self.optimize:
            flags.append('noopt')
        if not self.strip:
            flags.append('nostrip')
        if not self.docs:
            flags.append('nodocs')
        if self.parallel > 1:
            flags.append('parallel=%i' % self.parallel)
        return quote(' '.join(flags))

    def __repr__(self):
        attrs = ('check', 'optimize', 'strip', 'docs', 'parallel')
        params = ['%s=%r' % (attr, getattr(self, attr, None)) for attr in attrs]  # noqa
        return '<%s(%s)>' % (self.__class__.__name__, ' '.join(params))


class EnvBuilder(object):
    def set_arguments(self, parser):
        parser.add_argument('--no-check',
                            dest='check',
                            action='store_false',
                            help='not build-time test')
        parser.add_argument('--no-optimization',
                            dest='optimize',
                            action='store_false',
                            help='no optimization')
        parser.add_argument('--no-strip',
                            dest='strip',
                            action='store_false',
                            help='keep debugging symbols into the binary')

    def parse(self, parsed_args):
        build_options = BuildOptionsParam(
            check=parsed_args.check,
            optimize=parsed_args.optimize,
            strip=parsed_args.strip
        )
        env = {
            build_options.name: build_options
        }
        return env


def inline(env):
    results = []
    for key, value in env.items():
        if value is None:
            value = ''
        if not getattr(value, 'safe', False):
            value = quote(value)
        results.append('%s=%s' % (key, value))
    return ', '.join(results)
