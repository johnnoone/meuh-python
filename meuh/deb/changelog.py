"""
    meuh.deb.changelog
    ~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

import re
from .util import iter_src

FIRST_REGEX = re.compile(r'''
    (?P<name>\S+)\s+
    \((?P<version>.+?)\)\s+
    (?P<component>.+?);\s+
    urgency=(?P<urgency>.+?)$
''', re.X)

LAST_REGEX = re.compile(r'''\s--\s+
    (?P<maintainer>.+)?\s+
    <(?P<email>.+?)>\s{2,}
    (?P<date>.+?)$
''', re.X)


class Changelog(object):
    @classmethod
    def parse(cls, obj):
        logs = [Log.load(data) for data in load(obj)]
        instance = cls()
        instance.logs = logs
        return instance


class Log(object):
    name = None
    version = None
    component = None

    @classmethod
    def load(cls, obj):
        instance = cls()
        instance.name = obj.pop('name')
        instance.version = Version.parse(obj.pop('version'))
        instance.component = obj.pop('component')
        instance.urgency = obj.pop('urgency')
        return instance

    def __repr__(self):
        return '<%s(name=%r, version=%r, component=%r, urgency=%r)>' % (
            self.__class__.__name__,
            self.name,
            self.version,
            self.component,
            self.urgency
        )


class Version(object):
    epoch = None
    upstream = None
    revision = None

    def __init__(self, version):
        if isinstance(version, Version):
            epoch = version.epoch
            upstream = version.upstream
            revision = version.revision
        else:
            epoch, _, remains = version.rpartition(':')
            upstream, _, revision = version.partition('-')
        self.epoch = epoch if epoch != '' else None
        self.upstream = upstream
        self.revision = revision if revision != '' else None

    @classmethod
    def parse(cls, obj):
        return cls(obj)

    def __str__(self):
        response = ''
        if self.epoch is not None:
            response += '%s:' % self.epoch
        response += self.upstream
        if self.revision is not None:
            response += '-%s' % self.revision
        return response

    def __repr__(self):
        return '<%s(%r)>' % (self.__class__.__name__, self.__str__())


def load(obj):
    logs = []
    change = {}
    log = None

    for line in iter_src(obj):
        if not line:
            continue

        matches = FIRST_REGEX.match(line)
        if matches:
            # first line, parse it
            change.update(matches.groupdict())
            change.setdefault('logs', [])
            continue

        if line.startswith('  * '):
            if log:
                change['logs'].append(log)
            log = line[4:]
            continue

        if line.startswith('    '):
            log += '\n' + line[4:]
            continue

        matches = LAST_REGEX.match(line)
        if matches:
            if log:
                change['logs'].append(log)
            change.update(matches.groupdict())

            logs.append(change)
            change = {}
            log = None
            continue

    if change:
        logs.append(change)
        change = {}
        log = None

    return logs
