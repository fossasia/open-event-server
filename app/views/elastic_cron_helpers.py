"""
WARNING: This file contains cron jobs for elasticsearch, please use pure
python for any kind of operation here, Objects requiring flask app context may
not work properly

"""

from app.models.search.sync import rebuild_indices, sync
from app.views.celery_ import celery
from app.views.elastic_search import connect_from_config
from app.views.postgres import get_session_from_config

# Elasticsearch connection
es_store = connect_from_config()

# Postgres connection
session = get_session_from_config()


@celery.task(name='rebuild.events.elasticsearch')
def cron_rebuild_events_elasticsearch():
    "Re-inserts all eligible events into elasticsearch, deletes existing events"
    rebuild_indices(client=es_store, session=session)


def sync_events_elasticsearch():
    "Sync all newly created, updated or deleted events"
    sync()
