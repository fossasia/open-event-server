import unicodedata
from flask import Blueprint
from flask import request, jsonify
from flask import url_for, redirect, flash, render_template
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from flask.ext.login import current_user
from flask.ext.restplus import abort
from sqlalchemy_continuum import transaction_class

from app.helpers.data import delete_from_db, DataManager, save_to_db
from app.helpers.data import trash_user, restore_user
from app.helpers.data_getter import DataGetter
from app.helpers.ticketing import TicketingManager
from app.models.email_notifications import EmailNotification
from app.models.event import Event
from app.views.super_admin import USERS, check_accessible, list_navbar

sadmin_users = Blueprint('sadmin_users', __name__, url_prefix='/admin/users')


def get_or_create_notification_settings(event_id, user_id):
    email_notification = DataGetter \
        .get_email_notification_settings_by_event_id(user_id, event_id)
    if email_notification:
        return email_notification
    else:
        email_notification = EmailNotification(next_event=1,
                                               new_paper=1,
                                               session_schedule=1,
                                               session_accept_reject=1,
                                               after_ticket_purchase=1,
                                               user_id=current_user.id,
                                               event_id=event_id)
        return email_notification


@sadmin_users.before_request
def verify_accessible():
    return check_accessible(USERS)


@sadmin_users.route('/')
def index_view():
    active_user_list = []
    trash_user_list = []
    all_user_list = []
    active_users = DataGetter.get_active_users()
    trash_users = DataGetter.get_trash_users()
    all_users = DataGetter.get_all_users()
    custom_sys_roles = DataGetter.get_custom_sys_roles()
    for user in all_users:
        event_roles = DataGetter.get_event_roles_for_user(user.id)
        all_user_list.append({
            'user': user,
            'event_roles': event_roles}
        )
    for user in active_users:
        event_roles = DataGetter.get_event_roles_for_user(user.id)
        active_user_list.append({
            'user': user,
            'event_roles': event_roles, }
        )
    for user in trash_users:
        event_roles = DataGetter.get_event_roles_for_user(user.id)
        trash_user_list.append({
            'user': user,
            'event_roles': event_roles, }
        )
    return render_template('gentelella/super_admin/users/users.html',
                           active_user_list=active_user_list,
                           trash_user_list=trash_user_list,
                           all_user_list=all_user_list,
                           custom_sys_roles=custom_sys_roles,
                           navigation_bar=list_navbar())


@sadmin_users.route('/<user_id>/events/')
def user_events(user_id):
    live_events = DataGetter.get_live_events_of_user(user_id)
    draft_events = DataGetter.get_draft_events_of_user(user_id)
    past_events = DataGetter.get_past_events_of_user(user_id)
    all_events = DataGetter.get_all_events_of_user(user_id)
    imported_events = DataGetter.get_imports_by_user(user_id)
    all_ticket_stats = {}
    for event in all_events:
        all_ticket_stats[event.id] = TicketingManager.get_ticket_stats(event)

    return render_template('gentelella/users/events/index.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events,
                           imported_events=imported_events,
                           all_ticket_stats=all_ticket_stats)


@sadmin_users.route('/<user_id>/sessions/')
def user_sessions(user_id):
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    upcoming_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=True, user_id=user_id)
    speakers = DataGetter.get_speakers(1)
    im_config = DataGetter.get_image_configs()
    im_size = ''
    for config in im_config:
        if config.page == 'mysession':
            im_size = config.size
    past_events_sessions = DataGetter.get_sessions_of_user(upcoming_events=False, user_id=user_id)
    admin_access = 1
    page_content = {"tab_upcoming_events": "Upcoming Sessions",
                    "tab_past_events": "Past Sessions",
                    "title": "My Session Proposals"}
    return render_template('gentelella/users/mysessions/mysessions_list.html',
                           upcoming_events_sessions=upcoming_events_sessions, past_events_sessions=past_events_sessions,
                           page_content=page_content, placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder, im_size=im_size, speakers = speakers,
                           admin_access=admin_access)


@sadmin_users.route('/<user_id>/tickets/')
def user_tickets(user_id):
    page_content = {"tab_upcoming_events": "Upcoming Events",
                    "tab_past_events": "Past Events",
                    "title": "My Tickets"}

    upcoming_events_orders = TicketingManager.get_orders_of_user(user_id=user_id, upcoming_events=True)
    past_events_orders = TicketingManager.get_orders_of_user(user_id=user_id, upcoming_events=False)
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    im_config = DataGetter.get_image_configs()
    im_size = ''
    for config in im_config:
        if config.page == 'mysession':
            im_size = config.size

    return render_template('gentelella/users/mytickets/mytickets_list.html',
                           page_content=page_content,
                           upcoming_events_orders=upcoming_events_orders,
                           past_events_orders=past_events_orders,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           im_size=im_size)


@sadmin_users.route('/<user_id>/settings/')
def settings_view(user_id):
    return redirect(url_for('.contact_info_view', user_id=user_id))


@sadmin_users.route('/<user_id>/settings/contact-info/', methods=('POST', 'GET'))
def contact_info_view(user_id):
    if request.method == 'POST':
        DataManager.update_user(request.form, int(user_id), contacts_only_update=True)
        flash("Your contact info has been updated.", "success")
        return redirect(url_for('.contact_info_view', user_id=user_id))
    user = DataGetter.get_user(int(user_id))
    user.admin_access = 1

    return render_template('gentelella/users/settings/pages/contact_info.html', user=user)


@sadmin_users.route('/<user_id>/settings/email-preferences/')
def email_preferences_view(user_id):
    events = DataGetter.get_all_events()
    message_settings = DataGetter.get_all_message_setting()
    settings = DataGetter.get_email_notification_settings(user_id)
    user = DataGetter.get_user(int(user_id))
    user.admin_access = 1
    return render_template('gentelella/users/settings/pages/email_preferences.html',
                           settings=settings, events=events, message_settings=message_settings, user=user)


@sadmin_users.route('/<user_id>/settings/applications/')
def applications_view(user_id):
    user = DataGetter.get_user(int(user_id))
    user.admin_access = 1
    return render_template('gentelella/users/settings/pages/applications.html', user=user)


@sadmin_users.route('/<user_id>/settings/email/toggle/', methods=('POST',))
def email_toggle_view(user_id):
    if request.method == 'POST':
        name = request.form.get('name')
        value = int(request.form.get('value'))
        event_id = request.form.get('event_id')

        message = ''

        if name == 'global_email':
            ids = DataManager.toggle_email_notification_settings(user_id, value)
        else:
            name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
            email_notification = get_or_create_notification_settings(event_id, user_id)
            setattr(email_notification, name, value)
            save_to_db(email_notification, "EmailSettings Toggled")
            ids = [email_notification.id]

        return jsonify({
            'status': 'ok',
            'message': message,
            'notification_setting_ids': ids
        })


@sadmin_users.route('/<user_id>/settings/password/', methods=('POST', 'GET'))
def password_view(user_id):
    user = DataGetter.get_user(int(user_id))
    if request.method == 'POST':
        if user.password == generate_password_hash(request.form['current_password'], user.salt):
            if request.form['new_password'] == request.form['repeat_password']:
                salt = generate_random_salt()
                user.password = generate_password_hash(request.form['new_password'], salt)
                user.salt = salt
                save_to_db(user, "password changed")
                flash('The password of the user has been changed. Do inform him..', 'success')
            else:
                flash('The new password and the repeat don\'t match.', 'danger')
        else:
            flash('The current password is incorrect.', 'danger')

    user.admin_access = 1
    return render_template('gentelella/users/settings/pages/password.html', user=user)


@sadmin_users.route('/<user_id>/edit/', methods=('GET', 'POST'))
def edit_view(user_id):
    return redirect(url_for('.index_view'))


@sadmin_users.route('/<user_id>/update-roles/', methods=('GET', 'POST'))
def update_roles_view(user_id):
    if current_user.is_super_admin:
        user = DataGetter.get_user(user_id)
        user.is_admin = request.form.get('admin') == 'yes'
        save_to_db(user)

        custom_sys_roles = DataGetter.get_custom_sys_roles()
        for role in custom_sys_roles:
            field = request.form.get('custom_role-{}'.format(role.id))
            if field:
                DataManager.get_or_create_user_sys_role(user, role)
            else:
                DataManager.delete_user_sys_role(user, role)

        return redirect(url_for('.index_view'))
    else:
        abort(403)


@sadmin_users.route('/<user_id>/', methods=('GET', 'POST'))
def details_view(user_id):
    profile = DataGetter.get_user(user_id)
    return render_template('gentelella/users/profile/index.html',
                           profile=profile, user_id=user_id)


@sadmin_users.route('/<user_id>/trash/', methods=('GET',))
def trash_view(user_id):
    profile = DataGetter.get_user(user_id)
    if profile.is_super_admin:
        abort(403)
    trash_user(user_id)
    flash("User" + user_id + " has been deleted.", "danger")
    return redirect(url_for('.index_view'))


@sadmin_users.route('/<user_id>/restore/', methods=('GET',))
def restore_view(user_id):
    restore_user(user_id)
    flash("User" + user_id + " has been restored.", "success")
    return redirect(url_for('.index_view'))


@sadmin_users.route('/<user_id>/delete/', methods=('GET',))
def delete_view(user_id):
    profile = DataGetter.get_user(user_id)
    if profile.is_super_admin:
        abort(403)
    if request.method == "GET":
        transaction = transaction_class(Event)
        transaction.query.filter_by(user_id=user_id).delete()
        delete_from_db(profile, "User's been permanently removed")
    flash("User" + user_id + " has been permanently deleted.", "danger")
    return redirect(url_for('.index_view'))
