from flask import request, url_for
from flask_rest_jsonapi import ResourceList
from flask_rest_jsonapi.pagination import add_pagination_links
from flask_rest_jsonapi.querystring import QueryStringManager as QSManager
from sqlalchemy import desc, func

from app.api.bootstrap import api
from app.api.schema.event_locations import EventLocationSchema
from app.models import db
from app.models.event import Event
from app.models.event_location import EventLocation


class EventLocationList(ResourceList):

    """
    List event locations
    """

    def get(self, *args, **kwargs):
        qs = QSManager(request.args, self.schema)
        popular_locations = (
            db.session.query(
                Event.searchable_location_name, func.count(Event.id).label('counts')
            )
            .group_by(Event.searchable_location_name)
            .order_by(desc('counts'))
            .limit(6)
        )
        locations = []
        for location, _ in popular_locations:
            if location is not None:
                new_location = EventLocation(name=location)
                new_location.id = len(locations)
                locations.append(new_location)
        schema = EventLocationSchema()
        result = schema.dump(locations, many=True).data
        view_kwargs = (
            request.view_args if getattr(self, 'view_kwargs', None) is True else {}
        )
        add_pagination_links(
            result, len(locations), qs, url_for(self.view, **view_kwargs)
        )
        result.update({'meta': {'count': len(locations)}})
        return result

    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = EventLocationSchema
    data_layer = {'session': db.session, 'model': EventLocation}
