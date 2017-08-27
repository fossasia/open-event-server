from flask.ext.elasticsearch import FlaskElasticsearch
from elasticsearch import helpers
from app.models.event import Event


es = FlaskElasticsearch()


@celery.task(name='send.email.post')
def refresh_elasticsearch():
    events = Event.query.filter(Event.state == 'published', Event.deleted_at is None)
    event_data = ({'_type': 'event',
                   '_index': 'events',
                   '_id': event.id,
                   'name': event.name,
                   'description': event.description or None,
                   'searchable_location_name': event.searchable_location_name or None,
                   'organizer_name': event.organizer_name or None,
                   'organizer_description': event.organizer_description or None} for event in events)
    es.indices.delete('events')
    es.indices.create('events')
    helpers.bulk(es, event_data)
