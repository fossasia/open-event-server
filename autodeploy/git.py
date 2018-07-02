import logging
from command import execute

logger = logging.getLogger(__name__)


class GitError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.errors = errors

    def __str__(self):
        return '{}:\n {}'.format(self.message, self.errors)


def _git(cwd, *cmd):
    retcode, out, err = execute(cwd, '/usr/bin/git', *cmd)
    if retcode == 0:
        return out

    logger.error('git failed: %s', cwd)
    raise GitError('git exited with a non-zero exit code', err)


class Git():
    def __init__(self, repo, cwd, branch='master'):
        self.repo = repo
        self.cwd = cwd
        self.branch = branch
        self.clone_if_necessary()

    def clone_if_necessary(self):
        try:
            self.status()
        except GitError:
            logger.info('Cloning repo...')
            res = _git('.', 'clone', self.repo, self.cwd)
            logger.info('Cloned')
            return res

    def status(self):
        return _git(self.cwd, 'status', '-sb')

    def fetch(self):
        logger.info('Fetching from %s', self.branch)
        return _git(self.cwd, 'fetch', 'origin', self.branch)

    def pull(self):
        logger.info('Pulling in %s', self.cwd)
        return _git(self.cwd, 'pull', '--rebase')

    def changed_files(self):
        res = _git(self.cwd, 'diff', '--stat', 'origin/{}'.format(self.branch))
        last_line = res.splitlines()[-1]
        files_changed = int(last_line.split()[0])
        return files_changed


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    git = Git('..', branch='development')
    print('files changed: {}'.format(git.changed_files()))
