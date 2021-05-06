from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import current_user
from sqlalchemy import asc, distinct, func, or_

from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError
from app.api.helpers.mail import send_email
from app.api.helpers.permissions import is_coorganizer, jwt_required, to_event_id
from app.api.helpers.system_mails import MAILS, MailType
from app.api.helpers.utilities import group_by, strip_tags
from app.api.schema.exhibitors import ExhibitorReorderSchema
from app.api.schema.speakers import SpeakerReorderSchema
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.exhibitor import Exhibitor
from app.models.session import Session
from app.models.speaker import Speaker

events_routes = Blueprint('events_routes', __name__, url_prefix='/v1/events')


@events_routes.route('/<string:event_identifier>/sessions/dates')
@to_event_id
def get_dates(event_id):
    date_list = list(
        zip(
            *db.session.query(func.date(Session.starts_at))
            .distinct()
            .filter(
                Session.event_id == event_id,
                Session.starts_at != None,
                or_(Session.state == 'accepted', Session.state == 'confirmed'),
            )
            .order_by(asc(func.date(Session.starts_at)))
            .all()
        )
    )
    dates = list(
        map(
            str,
            date_list[0] if date_list else [],
        )
    )
    return jsonify(dates)


@events_routes.route('/<string:event_identifier>/contact-organizer', methods=['POST'])
@to_event_id
@jwt_required
def contact_organizer(event_id):
    event = Event.query.get_or_404(event_id)
    organizers_emails = list(
        set(
            list(map(lambda x: x.email, event.organizers))
            + list(map(lambda x: x.email, event.coorganizers))
        )
    )
    email = strip_tags(request.json.get('email'))
    context = {
        'attendee_name': current_user.fullname,
        'attendee_email': current_user.email,
        'event_name': event.name,
        'email': email,
    }
    organizer_mail = (
        "{attendee_name} ({attendee_email}) has a question for you about your event {event_name}: <br/><br/>"
        "<div style='white-space: pre-line;'>{email}</div>"
    )
    action = MailType.CONTACT_ORGANIZERS
    mail = MAILS[action]
    send_email(
        to=event.owner.email,
        action=action,
        subject=event.name + ": Question from " + current_user.fullname,
        html=organizer_mail.format(**context),
        bcc=organizers_emails,
        reply_to=current_user.email,
    )
    send_email(
        to=current_user.email,
        action=MailType.CONTACT_ORGANIZERS,
        subject=event.name + ": Organizers are succesfully contacted",
        html=render_template(
            mail['template'],
            event_name=event.name,
            email_copy=email,
        ),
    )
    return jsonify(
        success=True,
    )


@events_routes.route('/<string:event_identifier>/reorder-speakers', methods=['POST'])
@to_event_id
@is_coorganizer
def reorder_speakers(event_id):
    if 'reset' in request.args:
        updates = Speaker.query.filter(Speaker.event_id == event_id).update(
            {Speaker.order: 0}, synchronize_session=False
        )
        db.session.commit()

        return jsonify({'success': True, 'updates': updates})

    data, errors = SpeakerReorderSchema(many=True).load(request.json)
    if errors:
        raise UnprocessableEntityError(
            {'pointer': '/data', 'errors': errors}, 'Data in incorrect format'
        )

    speaker_ids = {item['speaker'] for item in data}
    event_ids = (
        db.session.query(distinct(Speaker.event_id))
        .filter(Speaker.id.in_(speaker_ids))
        .all()
    )

    if len(event_ids) != 1 or event_ids[0][0] != event_id:
        raise ForbiddenError(
            {'pointer': 'event_id'},
            'All speakers should be of single event which user has co-organizer access to',
        )

    result = group_by(data, 'order')
    updates = {}
    for (order, items) in result.items():
        speaker_ids = {item['speaker'] for item in items}
        result = Speaker.query.filter(Speaker.id.in_(speaker_ids)).update(
            {Speaker.order: order}, synchronize_session=False
        )
        updates[order] = result

    db.session.commit()

    return jsonify({'success': True, 'updates': updates})


@events_routes.route('/<string:event_identifier>/reorder-exhibitors', methods=['POST'])
@to_event_id
@is_coorganizer
def reorder_exhibitors(event_id):
    if 'reset' in request.args:
        updates = Exhibitor.query.filter(Exhibitor.event_id == event_id).update(
            {Exhibitor.position: 0}, synchronize_session=False
        )
        db.session.commit()

        return jsonify({'success': True, 'updates': updates})

    data, errors = ExhibitorReorderSchema(many=True).load(request.json)
    if errors:
        raise UnprocessableEntityError(
            {'pointer': '/data', 'errors': errors}, 'Data in incorrect format'
        )

    exhibitor_ids = {item['exhibitor'] for item in data}
    event_ids = (
        db.session.query(distinct(Exhibitor.event_id))
        .filter(Exhibitor.id.in_(exhibitor_ids))
        .all()
    )

    if len(event_ids) != 1 or event_ids[0][0] != event_id:
        raise ForbiddenError(
            {'pointer': 'event_id'},
            'All exhibitors should be of single event which user has co-organizer access to',
        )

    result = group_by(data, 'position')
    updates = {}
    for (position, items) in result.items():
        exhibitor_ids = {item['exhibitor'] for item in items}
        result = Exhibitor.query.filter(Exhibitor.id.in_(exhibitor_ids)).update(
            {Exhibitor.position: position}, synchronize_session=False
        )
        updates[position] = result

    db.session.commit()

    return jsonify({'success': True, 'updates': updates})


@events_routes.route(
    '/<string:event_identifier>/discount-codes/delete-unused', methods=['DELETE']
)
@to_event_id
@is_coorganizer
def delete_unused_discount_codes(event_id):
    query = DiscountCode.query.filter_by(event_id=event_id, orders=None)
    result = query.delete(synchronize_session=False)

    db.session.commit()

    return jsonify({'success': True, 'deletes': result})
