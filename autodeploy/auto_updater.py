from git import Git, GitError
from docker import DockerCompose, DockerComposeError

class AutoUpdater():
    def __init__(self, cwd, branch='master'):
        self.git = Git(cwd, branch)
        self.docker = DockerCompose(cwd)
