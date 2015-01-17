from setuptools import setup

setup(
    name='meuh',
    version='1.0',
    description='Create debian package with git, docker and love',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    install_requires=[
        # 'python-debian==0.1.23',
        'six==1.9.0',
        # 'deb-pkg-tools==1.29.3',
        'docker-py==0.7.1',
        'cliff==1.9.0'
    ],
    packages=['meuh'],
    package_data={
        'meuh.conf': ['*.cfg'],
    },
    entry_points={
        'console_scripts': [
            'meuh = meuh.cli:main',
        ],
        'meuh.commands': [
            'build = meuh.commands:BuildCommand',
            'distro_create = meuh.commands.distro:CreateCommand',
            'distro_list = meuh.commands.distro:ListCommand',
            'distro_show = meuh.commands.distro:ShowCommand',
            'builder_init = meuh.commands.builder:InitCommand',
            'builder_show = meuh.commands.builder:ShowCommand',
            'builder_stop = meuh.commands.builder:StopCommand',
        ]
    }
)
