import logging

from os.path import exists, isfile, join
from os import makedirs

from command import execute
from docker import DockerCompose, DockerComposeError
from git import Git

logger = logging.getLogger(__name__)


class AutoUpdater():
    def __init__(self, repo, cwd, branch='master'):
        if not exists(cwd):
            logger.info('Creating missing directory %s', cwd)
            makedirs(cwd)

        self.repo = repo
        self.cwd = cwd
        self.git = Git(repo, cwd, branch)
        self.docker = DockerCompose(cwd)

    def start(self):
        try:
            self.docker.start()
        except DockerComposeError as e:
            logger.warning('Start threw an error: %s', e.errors)

    def update(self):
        if True:  #self.git.changed_files() > 0:
            self.git.pull()
            self.docker.build()
            self.docker.restart()
            self.docker.exec('web', 'bash scripts/upgrade.sh')
            logger.info('update finished')

        return 'no update needed'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    a = AutoUpdater(
        'https://github.com/maxlorenz/open-event-server',
        '../../tmp/',
        branch='deployment')
    # logger.info('starting up')
    # print(a.docker.ps())
    # a.start()
    print(a.docker.ps())

    logger.info('updating')
    a.update()
