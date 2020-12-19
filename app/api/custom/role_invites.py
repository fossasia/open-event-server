import os
from flask import Blueprint, jsonify
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import ConflictError, ForbiddenError, NotFoundError
from app.api.helpers.mail import send_email_role_invite, send_user_email_role_invite
from app.api.helpers.permissions import jwt_required
from app.api.helpers.notification import send_notif_event_role
from app.api.helpers.permission_manager import has_access
from app.models.event import Event
from app.models.role_invite import RoleInvite
from app.models.user import User

role_invites_routes_blueprint = Blueprint('role_invites_routes', __name__, url_prefix='/v1/role-invites')

@role_invites_routes_blueprint.route(
    '/<int:role_invite_id>/resend-invite'
)
@jwt_required
def resend_invite(role_invite_id):
    role_invite = RoleInvite.query.get_or_404(role_invite_id)
    user = User.query.filter_by(email=role_invite.email).first()
    event = Event.query.filter_by(id=role_invite.event_id).first()
    frontend_url = get_settings()['frontend_url']
    link = "{}/e/{}/role-invites?token={}".format(
        frontend_url, event.identifier, role_invite.hash
    )
    if has_access('is_organizer', event_id=event.id):
        if user:
            send_user_email_role_invite(
                role_invite.email, role_invite.role_name, event.name, link
            )
            send_notif_event_role(user, role_invite.role_name, event.name, link, event.id)
        else:
            send_email_role_invite(
                role_invite.email, role_invite.role_name, event.name, link
            )
        return jsonify(
            status=True,
            message="invite is resend",
        )
    raise ForbiddenError({'source': ''}, "Organizer Access Required")
