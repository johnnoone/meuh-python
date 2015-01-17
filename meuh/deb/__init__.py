"""
    meuh.deb
    ~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Changelog', 'Control', 'ParseError', 'SourceControl',
           'parse_control', 'parse_source_control', 'parse_changelog']

import os
import os.path

from textwrap import dedent

from .changelog import Changelog
from .control import Control
from .exceptions import ParseError
from .source_control import SourceControl


def parse_control(obj):
    """Parses a control file

    :param data: representation of control file
    :type data: str or file handler
    :returns: Control
    """
    return Control.parse(obj)


def parse_changelog(obj):
    """Parses a changelog file

    :param data: representation of changelog file
    :type data: str or file handler
    :returns: Changelog
    """
    return Changelog.parse(obj)


def parse_source_control(obj):
    """Parses a .dsc file

    :param data: representation of .dsc file
    :type data: str or file handler
    :returns: Changelog
    """
    return SourceControl.parse(obj)


class Source(object):
    def __init__(self, src_dir):
        self.src_dir = src_dir
        with open(os.path.join(src_dir, 'debian/control')) as obj:
            data = obj.read().decode('utf-8')
            self.control = Control.parse(data)

        with open(os.path.join(src_dir, 'debian/changelog')) as obj:
            data = obj.read().decode('utf-8')
            self.changelog = Changelog.parse(data)

    @property
    def name(self):
        return self.control.general.source

    @property
    def build_depends(self):
        data = self.control.general.build_depends or ''
        return data.replace('\n', ' ')

    @property
    def build_depends_indep(self):
        data = self.control.general.build_depends_indep or ''
        return data.replace('\n', ' ')

    @property
    def build_conflicts(self):
        data = self.control.general.build_conflicts or ''
        return data.replace('\n', ' ')

    @property
    def build_conflicts_indep(self):
        data = self.control.general.build_conflicts_indep or ''
        return data.replace('\n', ' ')

    @property
    def version(self):
        name = self.name
        for log in self.changelog.logs:
            if name == log.name:
                return log.version


def build_control(src, arch=None):
    name = '%s-build-deps' % src.name
    depends = [
        'build-essential',
        src.build_depends,
        src.build_depends_indep
    ]
    depends = ', '.join(dep for dep in depends if dep)
    depends = 'Depends: %s' % depends if depends else ''

    conflicts = [
        src.build_conflicts,
        src.build_conflicts_indep
    ]
    conflicts = ', '.join(dep for dep in conflicts if dep)
    conflicts = 'Conflicts: %s' % conflicts if conflicts else ''

    version = src.version or '1.0'

    arch = arch or 'all'
    arch = arch if '[' in depends else 'all'

    return dedent("""\
    Section: devel
    Priority: optional
    Standards-Version: 3.7.3

    Package: {name}
    {depends}
    {conflicts}
    Version: {version}
    Architecture: {arch}
    Description: Install builds dependencies for {prog}
     Install builds dependencies for {prog}.
    """.format(name=name,
               depends=depends,
               conflicts=conflicts,
               version=version,
               arch=arch,
               prog=src.name))
