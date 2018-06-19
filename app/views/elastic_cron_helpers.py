from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

from app.models.event import Event
from app.models.search.event import SearchableEvent
from app.views.elastic_search import connect_from_config
from app.views.postgres import get_session_from_config
from app.views.celery_ import celery
from app.views.redis_store import redis_store

# WARNING: This file contains cron jobs for elasticsearch, please use pure
# python for any kind of operation here, Objects requiring flask app context
# may not work properly

# Elasticsearch connection
es_store = connect_from_config()

# Postgres connection
session = get_session_from_config()


@celery.task(name='rebuild.events.elasticsearch')
def cron_rebuild_events_elasticsearch():
    """
    Re-inserts all eligible events into elasticsearch
    Also clears event_index and event_delete redis sets
    :return:
    """
    redis_store.delete('event_index')
    redis_store.delete('event_delete')

    es_store.indices.delete(SearchableEvent.meta.index)
    SearchableEvent.init()  # Create ES index

    for event in session.query(Event):
        searchable = SearchableEvent()
        searchable.from_event(event)
        searchable.save()


def sync_events_elasticsearch():
    # Sync update and inserts
    updated, todo = 0, redis_store.scard('event_index')

    while updated < todo:
        updated += 1
        event_id = redis_store.spop('event_index')
        event = session.query(Event).filter(id=event_id).one()
        searchable = SearchableEvent()
        searchable.from_event(event)
        searchable.save()

    # sync both soft and hard deletes
    deleted, todo = 0, redis_store.scard('event_delete')

    while deleted < todo:
        deleted += 1
        event_id = redis_store.spop('event_delete')
        searchable = SearchableEvent()
        searchable.meta.id = event_id

        if event_id:  # For safety
            searchable.delete()
