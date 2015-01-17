__all__ = ['TestDeb']

import os.path
import unittest
from meuh import deb

HERE = os.path.dirname(os.path.abspath(__file__))

class TestDeb(unittest.TestCase):

    def test_control_error(self):
        with self.assertRaises(deb.ParseError):
            # expects str or file handler
            deb.parse_control(None)
        with self.assertRaises(deb.ParseError):
            # unknown fields
            deb.parse_control('foo: bar')
        with self.assertRaises(deb.ParseError):
            # cannot open filename
            deb.parse_control('control.txt')

    def test_control_str(self):
        parsed = deb.parse_control("""Source: bar\nbaz: qux""")

    def test_control_file(self):
        with open(os.path.join(HERE, 'nginx.control')) as file:
            parsed = deb.parse_control(file)

    def test_changelog_file(self):
        """docstring for test_changelog"""
        with open(os.path.join(HERE, 'nginx.changelog')) as file:
            parsed = deb.parse_changelog(file)
        assert False, parsed.logs

    def test_source_control_file(self):
        """docstring for test_changelog"""
        with open(os.path.join(HERE, 'nginx.dsc')) as file:
            parsed = deb.parse_source_control(file)
        assert False, parsed.logs
