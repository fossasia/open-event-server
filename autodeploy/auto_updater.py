import logging

from os.path import exists, isfile, join
from os import makedirs

from command import execute
from docker import DockerCompose, DockerComposeError
from git import Git

logger = logging.getLogger(__name__)


class AutoUpdater():
    def __init__(self, repo, cwd, branch='master'):
        self.repo = repo
        self.cwd = cwd
        self.git = Git(repo, cwd, branch)
        self.docker = DockerCompose(cwd)

        if not exists(cwd):
            logger.info('creating missing directory %s', cwd)
            makedirs(cwd)
            self.git.clone_if_necessary()
            self.first_startup()

    def first_startup(self):
        self.docker.build()
        self.docker.start()
        try:
            res = self.docker.exec('web', 'bash scripts/init.sh')
            logger.info('initialized with %s', res)
        except DockerComposeError as e:
            logger.warning('%s: %s', e.message, e.errors)
        self.upgrade()

    def start(self):
        try:
            self.docker.start()
        except DockerComposeError as e:
            logger.warning('Start threw an error: %s', e.errors)

    def update(self):
        if self.git.changed_files() > 0:
            self.git.pull()
            self.docker.build()
            self.docker.restart()
            logger.info('update finished')
        logger.info('no update needed')

    def upgrade(self):
        try:
            res = self.docker.exec('web', 'bash scripts/upgrade.sh')
            logger.info('upgraded with %s', res)
        except DockerComposeError as e:
            logger.warning('%s: %s', e.message, e.errors)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    a = AutoUpdater(
        'https://github.com/maxlorenz/open-event-server',
        '../../tmp/',
        branch='deployment')
    a.update()
    a.upgrade()
