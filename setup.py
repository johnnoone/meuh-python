#!/usr/bin/env python

from setuptools import setup

setup(
    name='meuh',
    version='0.1',
    description='Create debian package with git, docker and love',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    license='MIT',
    install_requires=[
        'cliff==1.9.0',
        'docker-py==0.7.1',
        'six==1.9.0',
    ],
    packages=['meuh'],
    entry_points={
        'console_scripts': [
            'meuh = meuh.cli:main',
        ],
        'meuh.commands': [
            'build = meuh.commands.build:BuildCommand',
            'publish = meuh.commands.build:PublishCommand',
            'destroy-all = meuh.commands.admin:DestroyAllCommand',
            'settings = meuh.commands.admin:SettingsCommand',
            'distro_init = meuh.commands.distro:InitCommand',
            'distro_list = meuh.commands.distro:ListCommand',
            'distro_show = meuh.commands.distro:ShowCommand',
            'distro_destroy = meuh.commands.distro:DestroyCommand',
            'distro_destroy-all = meuh.commands.distro:DestroyAllCommand',
            'bot_init = meuh.commands.bot:InitCommand',
            'bot_show = meuh.commands.bot:ShowCommand',
            'bot_destroy = meuh.commands.bot:DestroyCommand',
            'bot_destroy-all = meuh.commands.bot:DestroyAllCommand',
        ],
        'meuh.settings': [
            'load = meuh.commands.common:SettingsCommand'
        ]
    }
)
