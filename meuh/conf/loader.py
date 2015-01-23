from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['Loader']

import logging
import os.path

logger = logging.getLogger(__name__)


class Loader(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load(self, ini):
        results = {}
        results['docker'] = self.load_docker(ini)
        results['bots'] = self.load_bots(ini)
        results['distros'] = self.load_distros(ini)

        return results

    def load_docker(self, ini):
        results = {}

        section = 'docker'
        if ini.has_section(section):
            for key, value in ini.items(section):
                results[key] = value
        return results

    def load_bots(self, ini):
        defaults = {}
        results = {}

        section = 'bot'
        if ini.has_section(section):
            for key, value in ini.items(section):
                defaults[key] = value
        else:
            logger.warn('%s is not defined' % section)

        for section in ini.sections():
            if section.startswith('bot:'):
                name = section[4:]
                results[name] = self.load_bot(name, ini, defaults)
        return results

    def load_bot(self, name, ini, defaults=None):
        results = {}
        if defaults:
            for k, v in defaults.items():
                results.setdefault(k, v)

        section = 'bot:%s' % name
        if ini.has_section(section):
            for key, value in ini.items(section):
                results[key] = value
        else:
            logger.warn('%s is not defined' % section)

        if 'distro' not in results:
            raise ValueError('distro is required', name)

        if 'prereqs' in results:
            results['prereqs'] = [
                cmd for cmd in results['prereqs'].split('\n') if cmd
            ]
        else:
            results['prereqs'] = []

        if 'publish-commands' in results:
            results['publish-commands'] = [
                cmd for cmd in results['publish-commands'].split('\n') if cmd
            ]

        if 'build-commands' in results:
            results['build-commands'] = [
                cmd for cmd in results['build-commands'].split('\n') if cmd
            ]

        meta = {
            'bot': name,
            'distro': results['distro']
        }

        for key in ('build-dir', 'publish-dir'):
            results[key] = os.path.expanduser(results[key] % meta)

        return results

    def load_distros(self, ini):
        defaults = {}
        results = {}

        section = 'distro'
        if ini.has_section(section):
            for key, value in ini.items(section):
                defaults[key] = value
        else:
            logger.info('%s is not defined' % section)

        # env section has more priority than env option
        env = defaults.pop('env', {})

        section = 'env'
        if ini.has_section(section):
            for key, value in ini.items(section):
                env[key] = value
        else:
            logger.info('%s is not defined' % section)

        names = set()
        for section in ini.sections():
            if section.startswith('distro:'):
                names.add(section[7:])
            elif section.startswith('env:'):
                names.add(section[4:])
        for name in names:
            results[name] = self.load_distro(name, ini, defaults, env)
        return results

    def load_distro(self, name, ini, defaults=None, defaults_env=None):
        results = {}
        results.setdefault('tag', 'meuh/distro:%s' % name)

        if defaults:
            for k, v in defaults.items():
                results.setdefault(k, v)

        section = 'distro:%s' % name
        if ini.has_section(section):
            for key, value in ini.items(section):
                results[key] = value
        else:
            logger.warn('%s is not defined' % section)

        # env section has more priority than env option
        env = results.pop('env', {})

        if defaults_env:
            for k, v in defaults_env.items():
                env.setdefault(k, v)

        section = 'env:%s' % name
        if ini.has_section(section):
            for key, value in ini.items(section):
                env[key] = value
        else:
            logger.info('%s is not defined' % section)

        results['env'] = env

        if 'prereqs' in results:
            results['prereqs'] = [
                cmd for cmd in results['prereqs'].split('\n') if cmd
            ]
        else:
            results['prereqs'] = []

        if 'docker-file' in results:
            basename = results['docker-file']
            for filename in [os.path.expanduser(basename),
                             os.path.join(self.data_dir, basename)]:
                if os.path.exists(filename):
                    results['docker-file'] = filename
                    break

        return results

    def __call__(self, ini):
        return self.load(ini)
