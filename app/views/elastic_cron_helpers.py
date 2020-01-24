"""
WARNING: This file contains cron jobs for elasticsearch, please use pure
python for any kind of operation here, Objects requiring flask app context may
not work properly

"""

from app.api.helpers.tasks import celery
from app.models.event import Event
from app.models.search.sync import rebuild_indices, sync, sync_event_from_database
from app.views.elastic_search import connect_from_config
from app.views.postgres import get_session_from_config


@celery.task(name='rebuild.events.elasticsearch')
def cron_rebuild_events_elasticsearch():
    """Re-inserts all eligible events into elasticsearch, deletes existing events"""
    elastic = connect_from_config()
    session = get_session_from_config()
    rebuild_indices(client=elastic)

    for event in session.query(Event).filter_by(state='published'):
        sync_event_from_database(event)


def sync_events_elasticsearch():
    """Sync all newly created, updated or deleted events"""
    sync()
