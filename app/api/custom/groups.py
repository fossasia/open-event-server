from datetime import datetime

import pytz
from flask import Blueprint, jsonify
from flask_jwt_extended import current_user

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email_announce_event
from app.api.helpers.permissions import jwt_required, to_event_id
from app.models import user_follow_group
from app.models.event import Event
from app.models.group import Group
from app.models.user_follow_group import UserFollowGroup

groups_routes = Blueprint('groups_routes', __name__, url_prefix='/v1/groups')


@groups_routes.route('/<int:group_id>/events/<string:event_identifier>/announce')
@to_event_id
@jwt_required
def announce_event(group_id, event_id):
    group = Group.query.get_or_404(group_id)
    event = Event.query.get_or_404(event_id)
    if event.group_id != group.id:
        raise ForbiddenError({'source': 'event_id'}, "Event does not belong to the group")
    if group.user_id != current_user.id:
        raise ForbiddenError(
            {'source': 'user_id'}, "User have not permissions to announce event"
        )
    if event.is_announced:
        raise ForbiddenError({'source': 'event_id'}, "Event has already been announced")
    current_time = datetime.now(pytz.utc)
    if event.ends_at < current_time or event.state != "published":
        raise ForbiddenError(
            {'source': 'event_id'}, "Only upcoming and published events can be announced"
        )

    user_follow_groups = UserFollowGroup.query.filter_by(group_id=group.id).all()
    emails = set()
    for user_follow_group in user_follow_groups:
        emails.add(user_follow_group.user.email)

    send_email_announce_event(event, group, list(emails))

    event.is_announced = True

    save_to_db(event, 'Event is announced and save to db')

    return jsonify(
        success=True,
        message="Event Announced successfully",
    )
