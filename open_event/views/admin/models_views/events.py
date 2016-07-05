import json
import datetime

import pytz
from flask import request, flash
from flask.ext.restplus import abort
from flask.ext.admin import BaseView
from flask_admin import expose

from open_event import db
from open_event.helpers.permission_decorators import *
from open_event.helpers.helpers import fields_not_empty, string_empty
from ....helpers.data import DataManager, save_to_db, record_activity, delete_from_db, restore_event
from ....helpers.data_getter import DataGetter
from werkzeug.datastructures import ImmutableMultiDict
from open_event.helpers.helpers import send_event_publish

def is_verified_user():
    return login.current_user.is_verified


def is_accessible():
    return login.current_user.is_authenticated


class EventsView(BaseView):
    def _handle_view(self, name, **kwargs):
        if not is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        live_events = DataGetter.get_live_events()
        draft_events = DataGetter.get_draft_events()
        past_events = DataGetter.get_past_events()
        all_events = DataGetter.get_all_events()
        if not is_verified_user():
            flash("Your account is unverified. "
                  "Please verify by clicking on the confirmation link that has been emailed to you.")
        return self.render('/gentelella/admin/event/index.html',
                           live_events=live_events,
                           draft_events=draft_events,
                           past_events=past_events,
                           all_events=all_events)

    @expose('/create/<step>', methods=('GET', 'POST'))
    def create_view_stepped(self, step):
        return redirect(url_for('.create_view'))

    @expose('/create/', methods=('GET', 'POST'))
    def create_view(self,):
        if request.method == 'POST':
            img_files = []
            imd = ImmutableMultiDict(request.files)
            if 'sponsors[logo]' in imd and request.files['sponsors[logo]'].filename != "":
                for img_file in imd.getlist('sponsors[logo]'):
                    img_files.append(img_file)
            event = DataManager.create_event(request.form, img_files)
            if request.form.get('state', u'Draft') == u'Published' and string_empty(event.location_name):
                flash(
                    "Your event was saved. To publish your event please review the highlighted fields below.",
                    "warning")
                return redirect(url_for(
                    '.edit_view', event_id=event.id) + "#step=location_name")
            if event:
                return redirect(url_for('.details_view', event_id=event.id))
            return redirect(url_for('.index_view'))

        return self.render(
            '/gentelella/admin/event/new/new.html',
            start_date=datetime.datetime.now() + datetime.timedelta(days=10),
            event_types=DataGetter.get_event_types(),
            event_topics=DataGetter.get_event_topics(),
            event_sub_topics=DataGetter.get_event_subtopics(),
            timezones=DataGetter.get_all_timezones())

    @expose('/<int:event_id>/', methods=('GET', 'POST'))
    def details_view(self, event_id):
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
            checklist["2"] = 'missing_main'
        else:
            for sponsor in sponsors:
                if fields_not_empty(sponsor, ['name', 'description', 'url', 'level', 'logo']):
                    checklist["2"] = 'success'
                    break
                else:
                    checklist["2"] = 'missing_some'

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
        if not is_verified_user():
            flash("To make your event live, please verify your email by "
                  "clicking on the confirmation link that has been emailed to you.")

        return self.render('/gentelella/admin/event/details/details.html',
                           event=event,
                           checklist=checklist)

    @expose('/<event_id>/edit/', methods=('GET', 'POST'))
    @can_access
    def edit_view(self, event_id):
        return self.edit_view_stepped(event_id=event_id, step='')

    @expose('/<event_id>/edit/<step>', methods=('GET', 'POST'))
    @can_access
    def edit_view_stepped(self, event_id, step):
        event = DataGetter.get_event(event_id)
        session_types = DataGetter.get_session_types_by_event_id(event_id).all(
        )
        tracks = DataGetter.get_tracks(event_id).all()
        social_links = DataGetter.get_social_links_by_event_id(event_id)
        microlocations = DataGetter.get_microlocations(event_id).all()
        call_for_speakers = DataGetter.get_call_for_papers(event_id).first()
        sponsors = DataGetter.get_sponsors(event_id)
        custom_forms = DataGetter.get_custom_form_elements(event_id)
        speaker_form = json.loads(custom_forms.speaker_form)
        session_form = json.loads(custom_forms.session_form)

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
        print preselect

        if request.method == 'GET':
            return self.render('/gentelella/admin/event/edit/edit.html',
                               event=event,
                               session_types=session_types,
                               tracks=tracks,
                               social_links=social_links,
                               microlocations=microlocations,
                               call_for_speakers=call_for_speakers,
                               sponsors=sponsors,
                               event_types=DataGetter.get_event_types(),
                               event_topics=DataGetter.get_event_topics(),
                               event_sub_topics=DataGetter.get_event_subtopics(),
                               preselect=preselect,
                               timezones=DataGetter.get_all_timezones(),
                               step=step,
                               required=required)
        if request.method == "POST":
            img_files = []
            imd = ImmutableMultiDict(request.files)
            if 'sponsors[logo]' in imd and request.files['sponsors[logo]'].filename != "":
                for img_file in imd.getlist('sponsors[logo]'):
                    img_files.append(img_file)

            old_sponsor_logos = []
            old_sponsor_names = []
            for sponsor in sponsors:
                old_sponsor_logos.append(sponsor.logo)
                old_sponsor_names.append(sponsor.name)

            event = DataManager.edit_event(
                request, event_id, event, session_types, tracks, social_links,
                microlocations, call_for_speakers, sponsors, custom_forms, img_files, old_sponsor_logos, old_sponsor_names)


            if request.form.get('state',
                                u'Draft') == u'Published' and string_empty(
                                event.location_name):
                flash(
                    "Your event was saved. To publish your event please review the highlighted fields below.",
                    "warning")
                return redirect(url_for('.edit_view', event_id=event.id) + "#highlight=location_name")

            return redirect(url_for('.details_view', event_id=event_id))

    @expose('/<event_id>/trash/', methods=('GET',))
    @can_access
    def trash_view(self, event_id):
        if request.method == "GET":
            event = DataManager.trash_event(event_id)
        flash("Your event has been deleted.", "danger")
        if login.current_user.is_super_admin == True:
            return redirect(url_for('sadmin_events.index_view'))
        return redirect(url_for('.index_view'))

    @expose('/<event_id>/delete/', methods=('GET',))
    @is_super_admin
    def delete_view(self, event_id):
        if request.method == "GET":
            event = DataManager.delete_event(event_id)
        flash("Your event has been permanently deleted.", "danger")
        return redirect(url_for('sadmin_events.index_view'))

    @expose('/<event_id>/restore/', methods=('GET',))
    @is_super_admin
    def restore_event_view(self, event_id):
        restore_event(event_id)
        flash("Your event has been restored", "success")
        return redirect(url_for('sadmin_events.index_view'))

    @expose('/<int:event_id>/update/', methods=('POST',))
    def save_closing_date(self, event_id):
        event = DataGetter.get_event(event_id)
        event.closing_datetime = request.form['closing_datetime']
        save_to_db(event, 'Closing Datetime Updated')
        return self.render('/gentelella/admin/event/details/details.html',
                           event=event)


    @expose('/<int:event_id>/publish/', methods=('GET',))
    def publish_event(self, event_id):
        event = DataGetter.get_event(event_id)
        if string_empty(event.location_name):
            flash(
                "Your event was saved. To publish your event please review the highlighted fields below.",
                "warning")
            return redirect(url_for('.edit_view',
                                    event_id=event.id) + "#step=location_name")
        if not is_verified_user():
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

    @expose('/<int:event_id>/unpublish/', methods=('GET',))
    def unpublish_event(self, event_id):
        event = DataGetter.get_event(event_id)
        event.state = 'Draft'
        save_to_db(event, 'Event Unpublished')
        record_activity('publish_event', event_id=event.id, status='un-published')
        flash("Your event has been unpublished.", "warning")
        return redirect(url_for('.details_view', event_id=event_id))

    @expose('/<int:event_id>/restore/<int:version_id>', methods=('GET',))
    def restore_event_revision(self, event_id, version_id):
        event = DataGetter.get_event(event_id)
        version = event.versions[version_id]
        version.revert()
        db.session.commit()
        flash("Your event has been restored.", "success")
        return redirect(url_for('.details_view', event_id=event_id))

    @expose('/<int:event_id>/copy/', methods=('GET',))
    def copy_event(self, event_id):
        event = DataGetter.get_event(event_id)
        event.name = "Copy of " + event.name
        return self.render(
            '/gentelella/admin/event/new/new.html',
            event=event,
            is_copy=True,
            start_date=datetime.datetime.now() + datetime.timedelta(days=10),
            event_types=DataGetter.get_event_types(),
            event_topics=DataGetter.get_event_topics(),
            event_sub_topics=DataGetter.get_event_subtopics(),
            timezones=DataGetter.get_all_timezones())

    @expose('/<int:event_id>/role-invite/<hash>', methods=('GET', 'POST'))
    def user_role_invite(self, event_id, hash):
        event = DataGetter.get_event(event_id)
        user = login.current_user
        role_invite = DataGetter.get_event_role_invite(email=user.email,
                                                       event_id=event.id,
                                                       hash=hash)

        if role_invite:
            if role_invite.has_expired():
                delete_from_db(role_invite, 'Deleted RoleInvite')

                flash('Sorry, the invitation link has expired.', 'error')
                return redirect(url_for('.details_view', event_id=event.id))

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

    @expose('/<int:event_id>/role-invite/delete/<hash>', methods=('GET', 'POST'))
    @is_organizer
    def delete_user_role_invite(self, event_id, hash):
        event = DataGetter.get_event(event_id)
        role_invite = DataGetter.get_event_role_invite(event_id=event.id,
                                                       hash=hash)

        if role_invite:
            delete_from_db(role_invite, 'Deleted RoleInvite')

            flash('Invitation link has been successfully deleted.')
            return redirect(url_for('.details_view', event_id=event.id))
        else:
            abort(404)
