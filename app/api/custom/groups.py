from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import current_user

from app.api.helpers.mail import send_email
from app.api.helpers.permissions import jwt_required
from app.api.helpers.system_mails import MAILS, MailType
from app.api.helpers.utilities import strip_tags
from app.models.group import Group
from app.models.role import Role
from app.models.users_groups_role import UsersGroupsRoles

groups_routes = Blueprint('groups_routes', __name__, url_prefix='/v1/groups')


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
