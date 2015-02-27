import logging
import subprocess

logger = logging.getLogger(__name__)


class Response(object):
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def execute(cmd):
    logger.info('execute %s', cmd)

    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    stdout, stderr = proc.communicate()
    return Response(**{
        'returncode': proc.returncode,
        'stdout': stdout,
        'stderr': stderr
    })
