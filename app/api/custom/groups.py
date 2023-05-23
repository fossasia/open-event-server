from datetime import datetime

import pytz
from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import current_user

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email, send_email_announce_event
from app.api.helpers.permissions import jwt_required, to_event_id
from app.api.helpers.system_mails import MAILS, MailType
from app.api.helpers.utilities import strip_tags
from app.models.event import Event
from app.models.group import Group
from app.models.role import Role
from app.models.user_follow_group import UserFollowGroup
from app.models.users_groups_role import UsersGroupsRoles

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
            {'source': 'user_id'}, "User does not have permissions to announce event"
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


@groups_routes.route('/<int:group_id>/contact-organizer', methods=['POST'])
@jwt_required
def contact_group_organizer(group_id):
    group = Group.query.get_or_404(group_id)
    organizer_role = Role.query.filter_by(name='organizer').first()
    group_roles = UsersGroupsRoles.query.filter_by(
        group_id=group_id, role_id=organizer_role.id, accepted=True
    ).all()
    organizers_emails = list(set(list(map(lambda x: x.email, group_roles))))
    email = strip_tags(request.json.get('email'))
    context = {
        'attendee_name': current_user.fullname,
        'attendee_email': current_user.email,
        'group_name': group.name,
        'email': email,
    }
    organizer_mail = (
        "{attendee_name} ({attendee_email}) has a question for you about your group {group_name}: <br/><br/>"
        "<div style='white-space: pre-line;'>{email}</div>"
    )
    action = MailType.CONTACT_GROUP_ORGANIZERS
    mail = MAILS[action]
    send_email(
        to=group.user.email,
        action=action,
        subject=group.name + ": Question from " + current_user.fullname,
        html=organizer_mail.format(**context),
        bcc=organizers_emails,
        reply_to=current_user.email,
    )
    send_email(
        to=current_user.email,
        action=MailType.CONTACT_GROUP_ORGANIZERS,
        subject=group.name + ": Organizers are succesfully contacted",
        html=render_template(
            mail['template'],
            group_name=group.name,
            email_copy=email,
        ),
    )
    return jsonify(
        success=True,
    )
