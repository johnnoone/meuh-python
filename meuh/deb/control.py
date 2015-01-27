"""
    meuh.deb.control
    ~~~~~~~~~~~~~~~~

    .. see:: https://www.debian.org/doc/debian-policy/ch-controlfields.html

"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Control']

from .exceptions import ParseError, LoadError
from .util import iter_src


class Control(object):
    def __init__(self, general, binaries=None):
        self.general = general
        self.binaries = binaries or []

    @classmethod
    def parse(cls, obj):
        """Parse any obj.

        Obj must be a str or file handler file
        """
        paragraphs = load(obj)

        if not paragraphs:
            raise ParseError('Empty contents')
        try:
            return cls.load(paragraphs)
        except LoadError as error:
            raise ParseError(error)

    @classmethod
    def load(cls, obj):
        general = General.load(obj[0])
        binaries = []
        for paragraph in obj[1:]:
            binaries.append(Binary.load(paragraph))

        return cls(general, binaries)


class General(object):
    source = None

    @classmethod
    def load(cls, obj):
        instance = cls()
        try:
            instance.source = obj.pop('Source')
        except KeyError:
            raise LoadError('Source field is mandatory')
        instance.build_depends = obj.pop('Build-Depends', None)
        instance.build_depends_indep = obj.pop('Build-Depends-Indep', None)
        instance.build_conflicts = obj.pop('Build-Conflicts', None)
        instance.build_conflicts_indep = obj.pop('Build-Conflicts-Indep', None)
        return instance

    def __repr__(self):
        return '<%s(source=%r)>' % (self.__class__.__name__, self.source)


class Binary(object):
    package = None

    @classmethod
    def load(cls, obj):
        instance = cls()
        try:
            instance.package = obj.pop('Package')
        except KeyError:
            raise LoadError('Package field is mandatory')
        instance.architecture = obj.pop('Architecture', '')
        instance.depends = obj.pop('Depends', '')
        return instance

    def __repr__(self):
        return '<%s(package=%r)>' % (self.__class__.__name__, self.package)


def load(obj):
    paragraphs = []
    paragraph = {}
    field = None
    for line in iter_src(obj):
        if not line:
            # end of paragraph
            if paragraph:
                paragraphs.append(paragraph)
                paragraph = {}
                field = None
            continue

        if line[0] in ('#', '-'):
            # comments
            continue

        if line[0] in (' ', '\t'):
            value = line.strip()
            paragraph[field] += '\n' if value == '.' else ' '
            paragraph[field] += value
            continue

        if ':' in line:
            field, value = line.split(':', 1)
            field = field.strip()
            if field in paragraph:
                raise ParseError('field %s is already present' % field, line)
            paragraph[field] = value.strip()

    if paragraph and paragraph not in paragraphs:
        paragraphs.append(paragraph)

    return paragraphs
