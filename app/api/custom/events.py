from flask import Blueprint, jsonify, request
from sqlalchemy import asc, func, or_

from app.models import db
from app.models.session import Session
from app.models.event import Event
from app.api.helpers.mail import send_email
from app.models.mail import CONTACT_ORGANIZERS
from flask_jwt_extended import current_user
from app.api.helpers.permissions import jwt_required

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

@events_routes.route('/<int:event_id>/contact-organizer', methods=['POST'])
@jwt_required
def resend_invite(event_id):
    event = Event.query.get_or_404(event_id)
    organizers_emails = list(map(lambda x: x.email, event.organizers)) + list(map(lambda x: x.email, event.coorganizers))
    context = {
        'attendee_name': current_user.fullname,
        'attendee_email': current_user.email,
        'event_name': event.name,
    }
    organizer_mail = "{attendee_name} ({attendee_email}) has a question for you about your event {event_name} </br>" + request.json.get('email')
    attendee_mail = "Hello, you have contacted the organizers of the event {event_name}. Below you find a copy of your email. Organizers have received your message and will follow up with you. This is a system message. Please do not reply to this message. Replies are not monitored. Thank you."
    send_email(
        to=event.owner.email,
        action=CONTACT_ORGANIZERS,
        subject="You are contacted by " + current_user.fullname,
        html=organizer_mail.format(**context),
        bcc=organizers_emails
    )
    send_email(
        to=current_user.email,
        action=CONTACT_ORGANIZERS,
        subject="Organizers are succesfully contacted",
        html=attendee_mail.format(**context)
    )
    return jsonify(
        status=True,
        message="email is resend",
    )
