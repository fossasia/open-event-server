import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elasticsearch import helpers, Elasticsearch
from elasticsearch_dsl.connections import connections

from app.views.celery_ import celery
from app.views.redis_store import redis_store
from app.models.event import Event
from app.models.search.event import SearchableEvent
from config import Config

# WARNING: This file contains cron jobs for elasticsearch, please use pure python for any kind of operation here,
# Objects requiring flask app context may not work properly

es_store = Elasticsearch([Config.ELASTICSEARCH_HOST])
connections.create_connection(es_store)

db = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker()
Session.configure(bind=db)
session = Session()


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
    SearchableEvent.init()

    for event in session.query(Event):
        print('adding to elasticsearch:', event.name)
        searchable = SearchableEvent()
        searchable.from_event(event)
        searchable.save()


def sync_events_elasticsearch():
    # Sync update and inserts
    updated, todo = 1, redis_store.scard('event_index')

    while updated < todo:
        updated += 1
        event_id = redis_store.spop('event_index')
        event = session.query(Event).filter(id=event_id).one()
        searchable = SearchableEvent()
        searchable.from_event(event)
        searchable.save()

    # sync both soft and hard deletes
    deleted, todo = 1, redis_store.scard('event_delete')

    while deleted < todo:
        deleted += 1
        event_id = redis_store.scard('event_delete')
        searchable = SearchableEvent()
        searchable.meta.id = event_id
        searchable.delete()
