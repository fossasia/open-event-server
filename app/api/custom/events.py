from flask import Blueprint, jsonify
from sqlalchemy import asc, func, or_

from app.models import db
from app.models.session import Session

events_routes = Blueprint('events_routes', __name__, url_prefix='/v1/events')


@events_routes.route('/<int:event_id>/sessions/dates')
def get_dates(event_id):
    dates = (
        list(map(str, list(zip(
            *db.session.query(func.date(Session.starts_at))
            .distinct()
            .filter(Session.event_id==event_id, Session.starts_at != None, or_(Session.state == 'accepted', Session.state == 'confirmed'))
            .order_by(asc(func.date(Session.starts_at)))
            .all()
        ))[0]))
    )
    return jsonify(dates)
