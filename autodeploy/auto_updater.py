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
        except DockerComposeError:
            logger.warn('Start threw an error')

    def update(self):
        if self.git.changed_files() > 0:
            self.git.pull()
            self.docker.build()
            self.docker.restart()

            upgrade_script = join(self.cwd, 'scripts', 'upgrade.sh')
            if isfile(upgrade_script):
                logger.info('Executing upgrade script...')
                retcode, out, err = execute(self.cwd, '/bin/bash', '-c',
                                            upgrade_script)
                logger.info('Upgrade exited with %d', retcode)
            else:
                logger.info('No upgrade script found')

            return 'update finished'

        return 'no update needed'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    a = AutoUpdater('https://github.com/maxlorenz/open-event-server',
                    '../../tmp/', branch='deployment')
    a.start()
    a.update()
