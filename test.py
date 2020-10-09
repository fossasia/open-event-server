import json
from datetime import datetime

from app.api.helpers.db import get_count, get_or_create

# Admin message settings
from app.api.helpers.system_mails import MAILS
from app.api.helpers.utilities import strip_tags
from app.instance import current_app
from app.models import db

# User Permissions
from app.models.event import Event
from app.views.redis_store import redis_store

with current_app.app_context():
    query = Event.query.filter(
        Event.deleted_at == None,
        Event.state == 'published',
        Event.privacy == 'public',
        Event.owner != None,
        Event.starts_at != None,
        Event.ends_at != None,
    )
    print(f'Indexing { get_count(query) } Events:\n\n\n')
    for e in query.all():
        score = (
            1
            + get_count(e.orders_query)
            + get_count(e.speakers_query)
            + get_count(e.sessions_query)
        )
        longitude = e.longitude or 0
        latitude = e.latitude or 0
        data = {
            'id': e.id,
            'identifier': e.identifier,
            'name': e.name,
            'description': strip_tags(e.description or ''),
            'owner_name': e.owner.full_name,
            'score': score,
            'latitude': latitude,
            'longitude': longitude,
            'location_name': e.location_name or '',
            'location': f'{longitude},{latitude}',
            'starts_at': e.starts_at.timestamp(),
            'ends_at': e.ends_at.timestamp(),
        }
        # print(f'search:event:{e.id} ', data, '\n\n')
        redis_store.hset(f'search:event:{e.id}', mapping=data)

        # print('>>>', redis_store.execute_command('FT.SUGADD', 'sugg:event_name', e.name, score, 'INCR', 'PAYLOAD', json.dumps({ 'id': e.id, 'identifier': e.identifier })))
