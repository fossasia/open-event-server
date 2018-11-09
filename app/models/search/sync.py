"""
Sync full-text search indices with the database

- Mark events for later syncing
- Sync events
- Rebuild the indices
"""

import logging

from app.models.search.event import SearchableEvent
from app.views.elastic_search import client
from app.views.redis_store import redis_store

logger = logging.getLogger(__name__)

INDEX_CLASSES = [SearchableEvent]

REDIS_EVENT_INDEX = 'event_index'
REDIS_EVENT_DELETE = 'event_delete'


def sync_event_from_database(db_event):
    """Fetches the event with id `id` from the database and creates or updates the
    document in the Elasticsearch index

    """
    logger.info('Indexing event %i %s', db_event.id, db_event.name)

    searchable = SearchableEvent()
    searchable.from_event(db_event)
    searchable.save()


def rebuild_indices(client=client):
    """Rebuilds all search indices, deletes all data"""
    redis_store.delete(REDIS_EVENT_INDEX)
    redis_store.delete(REDIS_EVENT_DELETE)

    for index_class in INDEX_CLASSES:
        if client.indices.exists(index_class.meta.index):
            logger.info('Deleting index %s', index_class.meta.index)
            client.indices.delete(index_class.meta.index)

        index_class.init()


def delete_event_from_index(event_id):
    """Deletes an event from the Elasticsearch index"""
    searchable = SearchableEvent()
    searchable.id = event_id
    searchable.delete()


def mark_event(purpose, event_id):
    """Marks an event id in redis for later syncing.

    Purpose can be taken from this namespace (Look for global REDIS_X
    variables)

    """
    redis_store.sadd(purpose, event_id)


def _events_marked(purpose):
    """Retrieve all event ids from redis marked as `purpose`"""
    marked_event_id = redis_store.spop(purpose)
    while marked_event_id:
        yield marked_event_id
        marked_event_id = redis_store.spop(purpose)


def sync():
    """Syncs all events that have been marked"""
    logger.info('Syncing marked events')

    for event_id in list(_events_marked(REDIS_EVENT_INDEX)):
        logger.info('Syncing event %i', event_id)
        sync_event_from_database(event_id)

    for event_id in list(_events_marked(REDIS_EVENT_DELETE)):
        logger.info('Deleting event %i', event_id)
        delete_event_from_index(event_id)
