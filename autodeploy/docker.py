import logging
from docker_format import format_ps
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class DockerComposeError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.errors = errors

    def __str__(self):
        return '{}:\n {}'.format(self.message, self.errors)


def _docker_compose(cwd, *cmd):
    command = ['/usr/bin/docker-compose'] + list(cmd)
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd)
    out, err = process.communicate()

    if process.returncode == 0:
        return str(out, 'utf-8')

    logger.error('docker-compose command failed: %s', cwd)
    raise DockerComposeError(
        'Docker-Compose command exited with a non-zero exit code',
        str(err, 'utf-8'))


class DockerCompose():
    def __init__(self, cwd):
        self.cwd = cwd

    def ps(self):
        return _docker_compose(self.cwd, 'ps')

    def start(self):
        logger.info('starting up...')
        res = _docker_compose(self.cwd, 'start')
        logger.info('started')
        return res

    def stop(self):
        logger.info('stopping...')
        res = _docker_compose(self.cwd, 'stop')
        logger.info('stopped')
        return res
