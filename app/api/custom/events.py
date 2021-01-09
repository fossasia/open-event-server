from flask import Blueprint, jsonify
from sqlalchemy import or_
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.models.session import Session
from sqlalchemy import asc, func
from app.models import db

events_routes = Blueprint('events_routes', __name__, url_prefix='/v1/events')

@events_routes.route('/<string:event_identifier>/sessions/dates')
@jwt_required
def get_dates(event_identifier):
    event=Event.query.filter_by(identifier=event_identifier).first()
    dates = (
            list(map(str, list(zip(
                *db.session.query(func.date(Session.starts_at))
                .distinct()
                .filter(Session.event_id==event.id, Session.starts_at != None, or_(Session.state == 'accepted', Session.state == 'confirmed'))
                .order_by(asc(func.date(Session.starts_at)))
                .all()
            ))[0]))
    )
    return jsonify(dates)
