import logging
from os.path import join

import yaml
from celery import Celery

from auto_updater import AutoUpdater

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Celery()
cwd = '../../tmp'
projects = []

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


def get_auto_updater(name, cfg):
    logger.info('project <%s> from <%s> added', name, cfg['url'])
    a = AutoUpdater(cfg['url'], join(cwd, name), branch=cfg['branch'])
    if 'init' in cfg:
        a.add_init_script(cfg['init'])
    if 'upgrade' in cfg:
        a.add_upgrade_script(cfg['upgrade'])

    return a


def init_all_projects():
    projects = [get_auto_updater(n, config[n]) for n in config]

    for p in projects:
        p.start()


@app.task
def update_all_projects():
    for p in projects:
        p.update()
        p.upgrade()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0, update_all_projects(), name='update projects')


if __name__ == '__main__':
    init_all_projects()
    app.worker_main()
