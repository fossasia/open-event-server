import logging
import threading
from os.path import join

import yaml

from auto_updater import AutoUpdater

POLL_SECONDS = 60

logger = logging.getLogger(__name__)
log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

cwd = '../../tmp'

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


def get_auto_updater(name, cfg):
    logger.info('project <%s> from <%s> added', name, cfg['url'])
    a = AutoUpdater(
        name, cfg['url'], cwd=join(cwd, name), branch=cfg['branch'])

    if 'init' in cfg or 'upgrade' in cfg:
        a.add_scripts(
            container=cfg['container'],
            init_cmd=cfg['init'],
            upgrade_cmd=cfg['upgrade'])

    return a


projects = [get_auto_updater(n, config[n]) for n in config]


def start_all_projects():
    for p in projects:
        p.start()


def update_all_projects():
    for p in projects:
        logger.info('updating %s', p.repo)
        p.update()
        p.upgrade()

    logger.info('sleeping %d seconds', POLL_SECONDS)
    threading.Timer(POLL_SECONDS, update_all_projects).start()


if __name__ == '__main__':
    logger.info('starting projects')
    start_all_projects()
    logger.info('starting update threads for projects')
    update_all_projects()
