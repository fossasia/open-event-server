import psycopg2
from elasticsearch import helpers, Elasticsearch

from app.views.celery_ import celery
from app.views.redis_store import redis_store
from config import Config

# WARNING: This file contains cron jobs for elasticsearch, please use pure python for any kind of operation here,
# Objects requiring flask app context may not work properly

es_store = Elasticsearch([Config.ELASTICSEARCH_HOST])
conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)


@celery.task(name='rebuild.events.elasticsearch')
def cron_rebuild_events_elasticsearch():
    """
    Re-inserts all eligible events into elasticsearch
    Also clears event_index and event_delete redis sets
    :return:
    """
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, description, searchable_location_name, organizer_name, organizer_description FROM events WHERE state = 'published' and deleted_at is NULL ;")
    events = cur.fetchall()
    event_data = ({'_type': 'event',
                   '_index': 'events',
                   '_id': event_[0],
                   'name': event_[1],
                   'description': event_[2] or None,
                   'searchable_location_name': event_[3] or None,
                   'organizer_name': event_[4] or None,
                   'organizer_description': event_[5] or None}
                  for event_ in events)
    redis_store.delete('event_index')
    redis_store.delete('event_delete')
    es_store.indices.delete('events')
    es_store.indices.create('events')
    abc = helpers.bulk(es_store, event_data)
    print(abc)


class EventIterator:
    """
    Iterator that returns tuple with event info by popping the event id from the given redis set_name
    """
    def __init__(self, high, set_name):
        self.current = 1
        self.high = high
        self.set_name = set_name

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.high:
            raise StopIteration
        else:
            self.current += 1
            event_id = redis_store.spop(self.set_name)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, description, searchable_location_name, organizer_name, organizer_description FROM events WHERE id = %s;",
                (event_id,))
            event_ = cur.fetchone()
            return event_


def sync_events_elasticsearch():
    # Sync update and inserts
    index_count = redis_store.scard('event_index')
    index_event_data = ({'_type': 'event',
                         '_index': 'events',
                         '_id': event_[0],
                         'name': event_[1],
                         'description': event_[2] or None,
                         'searchable_location_name': event_[3] or None,
                         'organizer_name': event_[4] or None,
                         'organizer_description': event_[5] or None}
                        for event_ in EventIterator(index_count, 'event_index'))
    try:
        helpers.bulk(es_store, index_event_data)
    except Exception as e:
        print(e)

    # sync both soft and hard deletes
    del_count = redis_store.scard('event_delete')
    del_event_data = ({'_type': 'event',
                       '_index': 'events',
                       '_id': event_[0],
                       'name': event_[1],
                       'description': event_[2] or None,
                       'searchable_location_name': event_[3] or None,
                       'organizer_name': event_[4] or None,
                       'organizer_description': event_[5] or None}
                      for event_ in EventIterator(del_count, 'event_delete'))
    try:
        helpers.bulk(es_store, del_event_data)
    except Exception as e:
        print(e)
