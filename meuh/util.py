"""
    meuh.util
    ~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

__all__ = ['ensure_dir']

import os
import os.path
import logging
import subprocess
from glob import glob
logger = logging.getLogger(__name__)


def ensure_dir(path):
    """Ensure that path exists.
    """
    path = path.rstrip('/')
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info("created %s", path)
        return True
    return False


def copy_dir(source, destination, keep=False):
    ensure_dir(destination)
    for filename in glob(source):
        logger.debug('COPY %s to %s', filename, destination)
        if keep:
            cmd = ['rsync',
                   '--exclude=".git"',
                   '--exclude="~"',
                   '-v',
                   filename,
                   destination]
        else:
            cmd = ['rsync',
                   '--exclude=".git"',
                   '--exclude="~"',
                   '-v',
                   '--delete',
                   '-r',
                   filename,
                   destination]
        subprocess.call(cmd)
