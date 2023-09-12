from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import current_user
from sqlalchemy import asc, distinct, func, or_

from app.api.helpers.errors import ForbiddenError, NotFoundError, UnprocessableEntityError
from app.api.helpers.mail import send_email
from app.api.helpers.permissions import is_coorganizer, jwt_required, to_event_id
from app.api.helpers.system_mails import MAILS, MailType
from app.api.helpers.user import get_user_id_from_token, virtual_event_check_in
from app.api.helpers.utilities import group_by, strip_tags
from app.api.schema.exhibitors import ExhibitorReorderSchema
from app.api.schema.speakers import SpeakerReorderSchema
from app.api.schema.virtual_check_in import VirtualCheckInSchema
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.exhibitor import Exhibitor
from app.models.microlocation import Microlocation
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket_holder import TicketHolder

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


@events_routes.route('/<string:event_identifier>/attendees/search', methods=['GET'])
@to_event_id
@jwt_required
def search_attendees(event_id):
    """Search attendees by name or email."""
    query = TicketHolder.query.filter(TicketHolder.event_id == event_id)
    args = request.args
    if args.get('name'):
        query = query.filter(
            (TicketHolder.firstname.ilike('%' + args.get('name') + '%'))
            | (TicketHolder.lastname.ilike('%' + args.get('name') + '%'))
        )
    if args.get('email'):
        query = query.filter(TicketHolder.email.ilike('%' + args.get('email') + '%'))

    attendees = query.order_by(TicketHolder.id.desc()).all()

    return jsonify({'attendees': attendees})


@events_routes.route('/<string:event_identifier>/virtual/check-in', methods=['POST'])
@jwt_required
def virtual_check_in(event_identifier):
    """Search attendees by name or email."""
    event = db.session.query(Event).filter_by(identifier=event_identifier).first()
    if event is None:
        raise NotFoundError({'source': ''}, 'event can not be found')
    data, errors = VirtualCheckInSchema().load(request.get_json())
    if errors:
        raise UnprocessableEntityError(
            {'pointer': '/data', 'errors': errors}, 'Data in incorrect format'
        )
    token = None
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].split(" ")[1]
    if not token:
        return {
            "message": "Authentication Token is missing!",
            "data": None,
            "error": "Unauthorized",
        }, 401
    user_id = get_user_id_from_token(token)
    if user_id is None:
        return {"message": "Can't get user id!", "data": None}, 404

    if data.get('microlocation_id') is not None:
        microlocation = Microlocation.query.filter(
            Microlocation.id == data.get('microlocation_id')
        ).first()
        if microlocation is None:
            raise NotFoundError({'source': ''}, 'microlocation can not be found')

    orders = Order.query.filter(
        Order.user_id == user_id, Order.event_id == event.id
    ).all()

    orders_id = [order.id for order in orders]

    attendees = TicketHolder.query.filter(TicketHolder.order_id.in_(orders_id)).all()

    attendees_ids = [attendee.id for attendee in attendees]

    virtual_event_check_in(data, attendees_ids, event.id)

    return jsonify({'message': 'Attendee check in/out success'})


@events_routes.route('/<string:event_identifier>/sessions/languages', methods=['GET'])
@to_event_id
def get_languages(event_id):
    language_list = list(
        zip(
            *db.session.query(Session.language)
            .distinct()
            .filter(
                Session.event_id == event_id,
                Session.language != None,
            )
            .order_by(asc(Session.language))
            .all()
        )
    )
    languages = list(
        map(
            str,
            language_list[0] if language_list else [],
        )
    )
    return jsonify(languages)
