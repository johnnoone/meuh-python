#!/usr/bin/env python

from setuptools import setup

setup(
    name='meuh',
    version='0.1',
    description='Create debian package with git, docker and love',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    licence='MIT',
    install_requires=[
        'cliff==1.9.0'
        'docker-py==0.7.1',
        'six==1.9.0',
    ],
    packages=['meuh'],
    entry_points={
        'console_scripts': [
            'meuh = meuh.cli:main',
        ],
        'meuh.commands': [
            'settings = meuh.commands.common:SettingsCommand',
            'build = meuh.commands.build:BuildCommand',
            'publish = meuh.commands.build:PublishCommand',
            'distro_create = meuh.commands.distro:CreateCommand',
            'distro_list = meuh.commands.distro:ListCommand',
            'distro_show = meuh.commands.distro:ShowCommand',
            'bot_init = meuh.commands.bot:InitCommand',
            'bot_show = meuh.commands.bot:ShowCommand',
            'bot_stop = meuh.commands.bot:StopCommand',
        ],
        'meuh.settings': [
            'load = meuh.commands.common:SettingsCommand'
        ]
    }
)
