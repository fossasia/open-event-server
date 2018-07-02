import logging
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class GitError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.errors = errors

    def __str__(self):
        return '{}:\n {}'.format(self.message, self.errors)


def _git(cwd, *cmd):
    command = ['/usr/bin/git'] + list(cmd)
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd)
    out, err = process.communicate()

    if process.returncode == 0:
        return str(out, 'utf-8')

    logger.error('docker-compose command failed: %s', cwd)
    raise GitError('Git command exited with a non-zero exit code',
                   str(err, 'utf-8'))


class Git():
    def __init__(self, cwd, branch='master'):
        self.cwd = cwd
        self.branch = branch

    def status(self):
        return _git(self.cwd, 'status', '-sb')

    def fetch(self):
        logger.info('Fetching from %s', self.branch)
        return _git(self.cwd, 'fetch', 'origin', self.branch)

    def pull(self):
        logger.info('Pulling in %s', self.cwd)
        return _git(self.cwd, 'pull', '--rebase')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    git = Git('../open-event-server')
    print(git.status())
    print(git.fetch())
    print(git.pull())
