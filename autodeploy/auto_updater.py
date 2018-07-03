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

        self.upgrade_script = None
        self.init_script = None

        if not exists(cwd):
            logger.info('creating missing directory %s', cwd)
            makedirs(cwd)
            self.git.clone_if_necessary()
            self.first_startup()

    def add_init_script(self, command):
        self.init_script = command

    def add_upgrade_script(self, command):
        self.upgrade_script = command

    def first_startup(self):
        self.docker.update()
        if self.init_script:
            try:
                res = self.docker.exec('web', upgrade_script)
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
            self.docker.update()
            logger.info('update finished')
        logger.info('no update needed')

    def upgrade(self):
        if self.upgrade_script:
            try:
                res = self.docker.exec('web', self.upgrade_script)
                logger.info('upgraded with %s', res)
            except DockerComposeError as e:
                logger.warning('%s: %s', e.message, e.errors)
