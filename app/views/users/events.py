import binascii
import datetime
import json
import os
from uuid import uuid4

from flask import Blueprint
from flask import flash, url_for, redirect, request, jsonify, Markup, render_template
from flask.ext.login import current_user
from flask.ext.restplus import abort

from app import db
from app.helpers.auth import AuthManager
from app.helpers.data import DataManager, save_to_db, record_activity, delete_from_db, restore_event
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import fields_not_empty, string_empty, get_count
from app.helpers.helpers import send_event_publish
from app.helpers.helpers import uploaded_file
from app.helpers.invoicing import InvoicingManager
from app.helpers.microservices import AndroidAppCreator, WebAppCreator
from app.helpers.permission_decorators import is_organizer, is_super_admin, can_access
from app.helpers.storage import upload_local, UPLOAD_PATHS
from app.helpers.ticketing import TicketingManager
from app.helpers.wizard.clone import create_event_copy
from app.helpers.wizard.event import get_event_json, save_event_from_json
from app.helpers.wizard.helpers import get_current_timezone
from app.helpers.wizard.sessions_speakers import get_microlocations_json, get_session_types_json, get_tracks_json, \
    save_session_speakers
from app.helpers.wizard.sponsors import get_sponsors_json, save_sponsors_from_json
from app.models.call_for_papers import CallForPaper
from app.settings import get_settings


def get_random_hash():
    return binascii.b2a_hex(os.urandom(20))


events = Blueprint('events', __name__, url_prefix='/events')


@events.route('/')
def index_view():
    live_events = DataGetter.get_live_events_of_user()
    draft_events = DataGetter.get_draft_events_of_user()
    past_events = DataGetter.get_past_events_of_user()
    all_events = DataGetter.get_all_events_of_user()
    imported_events = DataGetter.get_imports_by_user()
    all_ticket_stats = {}
    for event in all_events:
        all_ticket_stats[event.id] = TicketingManager.get_ticket_stats(event)
    if not AuthManager.is_verified_user():
        flash(Markup('Your account is unverified. '
                     'Please verify by clicking on the confirmation link that has been emailed to you.'
                     '<br>Did not get the email? Please <a href="/resend_email/" class="alert-link"> '
                     'click here to resend the confirmation.</a>'))

    return render_template('gentelella/users/events/index.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events,
                           imported_events=imported_events,
                           all_ticket_stats=all_ticket_stats)


@events.route('/create/', defaults={'step': ''})
@events.route('/create/<step>')
def create_view(step):
    if step != '':
        return redirect(url_for('.create_view', step=''))

    hash = get_random_hash()
    if CallForPaper.query.filter_by(hash=hash).all():
        hash = get_random_hash()

    current_timezone = get_current_timezone()

    return render_template(
        'gentelella/users/events/wizard/wizard.html',
        current_date=datetime.datetime.now(),
        event_types=DataGetter.get_event_types(),
        event_licences=DataGetter.get_event_licences(),
        event_topics=DataGetter.get_event_topics(),
        event_sub_topics=DataGetter.get_event_subtopics(),
        timezones=DataGetter.get_all_timezones(),
        cfs_hash=hash,
        current_timezone=current_timezone,
        payment_countries=DataGetter.get_payment_countries(),
        payment_currencies=DataGetter.get_payment_currencies(),
        included_settings=get_module_settings())


@events.route('/create/files/image/', methods=['POST'])
def create_image_upload():
    if request.method == 'POST':
        image = request.form['image']
        if image:
            image_file = uploaded_file(file_content=image)
            image_url = upload_local(
                image_file,
                UPLOAD_PATHS['temp']['image'].format(uuid=uuid4())
            )
            return jsonify({'status': 'ok', 'image_url': image_url})
        else:
            return jsonify({'status': 'no_image'})


@events.route('/<event_id>/')
@can_access
def details_view(event_id):
    event = DataGetter.get_event(event_id)
    checklist = {"": ""}

    if fields_not_empty(event,
                        ['name', 'start_time', 'end_time', 'location_name',
                         'organizer_name', 'organizer_description']):
        checklist["1"] = 'success'
    elif fields_not_empty(event, ['name', 'start_time', 'end_time']):
        checklist["1"] = 'missing_some'
    else:
        checklist["1"] = 'missing_main'

    call_for_speakers = DataGetter.get_call_for_papers(event_id).first()
    if call_for_speakers:
        if fields_not_empty(call_for_speakers,
                            ['announcement', 'start_date', 'end_date']):
            checklist["4"] = "success"
        elif fields_not_empty(call_for_speakers,
                              ['start_date', 'end_date']):
            checklist["4"] = "missing_some"
        else:
            checklist["4"] = 'missing_main'
    else:
        checklist["4"] = "optional"

    sponsors = DataGetter.get_sponsors(event_id).all()
    if not sponsors:
        checklist["2"] = 'optional'
    else:
        for sponsor in sponsors:
            if fields_not_empty(sponsor, ['name', 'description', 'url', 'level', 'logo']):
                checklist["2"] = 'success'
                break
            else:
                checklist["2"] = 'missing_some'
    if event.has_session_speakers:
        session_types = DataGetter.get_session_types_by_event_id(event_id)
        tracks = DataGetter.get_tracks(event_id)
        microlocations = DataGetter.get_microlocations(event_id)

        if not session_types and not tracks and not microlocations:
            checklist["3"] = 'optional'
        elif not session_types or not tracks or not microlocations:
            checklist["3"] = 'missing_main'
        else:
            for session_type in session_types:
                if fields_not_empty(session_type, ['name', 'length']):
                    checklist["3"] = 'success'
                    break
                else:
                    checklist["3"] = 'missing_some'
            for microlocation in microlocations:
                if fields_not_empty(microlocation, ['name']):
                    checklist["3"] = 'success'
                    break
                else:
                    checklist["3"] = 'missing_some'
            for tracks in tracks:
                if fields_not_empty(tracks, ['name', 'color']):
                    checklist["3"] = 'success'
                    break
                else:
                    checklist["3"] = 'missing_some'

        checklist["5"] = 'success'
    else:
        checklist["3"] = 'optional'
        checklist["4"] = 'optional'
        checklist["5"] = 'optional'

    if not current_user.can_publish_event() and not AuthManager.is_verified_user():
        flash(Markup('To make your event live, please verify your email by '
                     'clicking on the confirmation link that has been emailed to you.<br>'
                     'Did not get the email? Please <a href="/resend_email/" class="alert-link"> click here to '
                     'resend the confirmation.</a>'))

    sessions = {'pending': get_count(DataGetter.get_sessions_by_state_and_event_id('pending', event_id)),
                'accepted': get_count(DataGetter.get_sessions_by_state_and_event_id('accepted', event_id)),
                'rejected': get_count(DataGetter.get_sessions_by_state_and_event_id('rejected', event_id)),
                'draft': get_count(DataGetter.get_sessions_by_state_and_event_id('draft', event_id))}

    return render_template('gentelella/users/events/details/details.html',
                           event=event,
                           checklist=checklist,
                           sessions=sessions,
                           settings=get_settings())


@events.route('/<event_id>/edit/', defaults={'step': ''})
@events.route('/<event_id>/edit/<step>/')
@can_access
def edit_view(event_id, step=''):
    event = DataGetter.get_event(event_id)
    custom_forms = DataGetter.get_custom_form_elements(event_id)
    speaker_form = json.loads(custom_forms.speaker_form)
    session_form = json.loads(custom_forms.session_form)
    call_for_speakers = DataGetter.get_call_for_papers(event_id).first()

    preselect = []
    required = []
    for session_field in session_form:
        if session_form[session_field]['include'] == 1:
            preselect.append(session_field)
            if session_form[session_field]['require'] == 1:
                required.append(session_field)
    for speaker_field in speaker_form:
        if speaker_form[speaker_field]['include'] == 1:
            preselect.append(speaker_field)
            if speaker_form[speaker_field]['require'] == 1:
                required.append(speaker_field)

    hash = get_random_hash()
    if CallForPaper.query.filter_by(hash=hash).all():
        hash = get_random_hash()

    current_timezone = get_current_timezone()

    seed = {
        'event': get_event_json(event),
        'sponsors': get_sponsors_json(event_id),
        'microlocations': get_microlocations_json(event_id),
        'sessionTypes': get_session_types_json(event_id),
        'tracks': get_tracks_json(event_id),
        'callForSpeakers': call_for_speakers.serialize if call_for_speakers else None
    }

    return render_template('gentelella/users/events/wizard/wizard.html',
                           event=event,
                           step=step,
                           seed=json.dumps(seed),
                           required=required,
                           preselect=preselect,
                           current_date=datetime.datetime.now(),
                           event_types=DataGetter.get_event_types(),
                           event_licences=DataGetter.get_event_licences(),
                           event_topics=DataGetter.get_event_topics(),
                           event_sub_topics=DataGetter.get_event_subtopics(),
                           timezones=DataGetter.get_all_timezones(),
                           call_for_speakers=call_for_speakers,
                           cfs_hash=hash,
                           current_timezone=current_timezone,
                           payment_countries=DataGetter.get_payment_countries(),
                           payment_currencies=DataGetter.get_payment_currencies(),
                           included_settings=get_module_settings(),
                           session_types=get_session_types_json(event_id),
                           microlocations=get_microlocations_json(event_id))


@events.route('/<event_id>/trash/')
@can_access
def trash_view(event_id):
    if request.method == "GET":
        DataManager.trash_event(event_id)
    flash("Your event has been deleted.", "danger")
    if current_user.is_super_admin:
        return redirect(url_for('sadmin_events.index_view'))
    return redirect(url_for('.index_view'))


@events.route('/<event_id>/delete/')
@is_super_admin
def delete_view(event_id):
    if request.method == "GET":
        DataManager.delete_event(event_id)
    flash("Your event has been permanently deleted.", "danger")
    return redirect(url_for('sadmin_events.index_view'))


@events.route('/<event_id>/restore/')
@is_super_admin
def restore_event_view(event_id):
    restore_event(event_id)
    flash("Your event has been restored", "success")
    return redirect(url_for('sadmin_events.index_view'))


@events.route('/<int:event_id>/publish/')
@can_access
def publish_event(event_id):
    event = DataGetter.get_event(event_id)
    if string_empty(event.location_name):
        flash(
            "Your event was saved. To publish your event please review the highlighted fields below.",
            "warning")
        return redirect(url_for('.edit_view',
                                event_id=event.id) + "#highlight=location_name")
    if not current_user.can_publish_event():
        flash("You don't have permission to publish event.")
        return redirect(url_for('.details_view', event_id=event_id))
    event.state = 'Published'
    save_to_db(event, 'Event Published')
    organizers = DataGetter.get_user_event_roles_by_role_name(event_id, 'organizer')
    speakers = DataGetter.get_user_event_roles_by_role_name(event_id, 'speaker')
    link = url_for('.details_view', event_id=event_id, _external=True)

    for organizer in organizers:
        send_event_publish(organizer.user.email, event.name, link)
    for speaker in speakers:
        send_event_publish(speaker.user.email, event.name, link)

    record_activity('publish_event', event_id=event.id, status='published')
    flash("Your event has been published.", "success")
    return redirect(url_for('.details_view', event_id=event_id))


@events.route('/<int:event_id>/unpublish/')
@can_access
def unpublish_event(event_id):
    event = DataGetter.get_event(event_id)
    event.state = 'Draft'
    save_to_db(event, 'Event Unpublished')
    record_activity('publish_event', event_id=event.id, status='un-published')
    flash("Your event has been unpublished.", "warning")
    return redirect(url_for('.details_view', event_id=event_id))


@events.route('/<int:event_id>/generate_android_app/', methods=['POST'])
@can_access
def generate_android_app(event_id):
    AndroidAppCreator(event_id).create()
    return redirect(url_for('.details_view', event_id=event_id))


@events.route('/<int:event_id>/generate_web_app/', methods=['POST'])
@can_access
def generate_web_app(event_id):
    WebAppCreator(event_id).create()
    return redirect(url_for('.details_view', event_id=event_id))


@events.route('/<int:event_id>/restore/<int:version_id>/')
@can_access
def restore_event_revision(event_id, version_id):
    event = DataGetter.get_event(event_id)
    version = event.versions[version_id]
    version.revert()
    db.session.commit()
    flash("Your event has been restored.", "success")
    return redirect(url_for('.details_view', event_id=event_id))


@events.route('/<int:event_id>/copy/')
@can_access
def copy_event(event_id):
    event = create_event_copy(event_id)
    return redirect(url_for('.edit_view', event_id=event.id))


@events.route('/<int:event_id>/role-invite/<hash>/', methods=['GET', 'POST'])
def user_role_invite(event_id, hash):
    """Accept User-Role invite for the event.
    """
    event = DataGetter.get_event(event_id)
    user = current_user
    role_invite = DataGetter.get_event_role_invite(event.id, hash,
                                                   email=user.email)

    if role_invite:
        if role_invite.has_expired():
            delete_from_db(role_invite, 'Deleted RoleInvite')

            flash('Sorry, the invitation link has expired.', 'error')
            return redirect(url_for('.details_view', event_id=event.id))

        if user.has_role(event.id):
            flash('You have already been assigned a Role in the Event.', 'warning')
            return redirect(url_for('events.details_view', event_id=event_id))

        role = role_invite.role
        data = dict()
        data['user_email'] = role_invite.email
        data['user_role'] = role.name
        DataManager.add_role_to_event(data, event.id)

        # Delete Role Invite after it has been accepted
        delete_from_db(role_invite, 'Deleted RoleInvite')

        flash('You have been added as a %s' % role.title_name)
        return redirect(url_for('.details_view', event_id=event.id))
    else:
        abort(404)


@events.route('/<int:event_id>/role-invite/decline/<hash>/', methods=['GET', 'POST'])
def user_role_invite_decline(event_id, hash):
    """Decline User-Role invite for the event.
    """
    event = DataGetter.get_event(event_id)
    user = current_user
    role_invite = DataGetter.get_event_role_invite(event.id, hash,
                                                   email=user.email)

    if role_invite:
        if role_invite.has_expired():
            delete_from_db(role_invite, 'Deleted RoleInvite')

            flash('Sorry, the invitation link has expired.', 'error')
            return redirect(url_for('.details_view', event_id=event.id))

        DataManager.decline_role_invite(role_invite)

        flash('You have declined the role invite.')
        return redirect(url_for('.details_view', event_id=event.id))
    else:
        abort(404)


@events.route('/<int:event_id>/role-invite/delete/<hash>/', methods=['GET', 'POST'])
@is_organizer
def delete_user_role_invite(event_id, hash):
    event = DataGetter.get_event(event_id)
    role_invite = DataGetter.get_event_role_invite(event.id, hash)

    if role_invite:
        delete_from_db(role_invite, 'Deleted RoleInvite')

        flash('Invitation link has been successfully deleted.')
        return redirect(url_for('.details_view', event_id=event.id))
    else:
        abort(404)


@events.route('/discount/apply/', methods=['POST'])
def apply_discount_code():
    discount_code = request.form['discount_code']
    discount_code = InvoicingManager.get_discount_code(discount_code)
    if discount_code:
        if discount_code.is_active:
            if InvoicingManager.get_discount_code_used_count(discount_code.id) >= discount_code.tickets_number:
                return jsonify({'status': 'error', 'message': 'Expired discount code'})
            return jsonify({'status': 'ok', 'discount_code': discount_code.serialize})
        else:
            return jsonify({'status': 'error', 'message': 'Expired discount code'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid discount code'})


@events.route('/save/<string:what>/', methods=['POST'])
def save_event_from_wizard(what):
    data = request.get_json()
    if 'event_id' not in data or not data['event_id']:
        event_id = None
    else:
        event_id = data['event_id']
        if not current_user.is_staff and not current_user.is_organizer(event_id) and not current_user.is_coorganizer(event_id):
            abort(403)
    if what == 'event':
        return jsonify(save_event_from_json(data, event_id))
    elif what == 'sponsors':
        return jsonify(save_sponsors_from_json(data))
    elif what == 'sessions-tracks-rooms':
        return jsonify(save_session_speakers(data))
    elif what == 'all':
        response = save_event_from_json(data['event'], event_id)
        save_sponsors_from_json(data['sponsors'], response['event_id'])
        save_session_speakers(data['session_speakers'], response['event_id'])
        return jsonify(response)
    else:
        abort(404)


def get_module_settings():
    included_setting = []
    module = DataGetter.get_module()
    if module is not None:
        if module.ticket_include:
            included_setting.append('ticketing')
        if module.payment_include:
            included_setting.append('payments')
        if module.donation_include:
            included_setting.append('donations')
    return included_setting
