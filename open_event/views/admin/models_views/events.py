import os

from flask import request, flash, url_for, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext import login

from open_event.helpers.permission_decorators import is_organizer
from ....helpers.data import DataManager, save_to_db
from ....helpers.data_getter import DataGetter
import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict

def string_empty(string):
    if type(string) is not str and type(string) is not unicode:
        return False
    if string and string.strip() and string != u'' and string != u' ':
        return False
    else:
        return True

def string_not_empty(string):
    return not string_empty(string)

def fields_not_empty(obj, fields):
    for field in fields:
        if string_empty(getattr(obj, field)):
            return False
    return True

class EventsView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        live_events = DataGetter.get_live_events()
        draft_events = DataGetter.get_draft_events()
        past_events = DataGetter.get_past_events()
        all_events = DataGetter.get_all_events()
        return self.render('/gentelella/admin/event/index.html',
                           live_events=live_events, draft_events=draft_events, past_events=past_events,
                           all_events=all_events)

    @expose('/create/', methods=('GET', 'POST'))
    def create_view(self):
        if request.method == 'POST':
            imd = ImmutableMultiDict(request.files)
            for img_file in imd.getlist('sponsors[logo]'):
                if img_file.filename != '':
                    filename = secure_filename(img_file.filename)
                    img_file.save(os.path.join(os.path.realpath('.') + '/static/media/image/', filename))
            event = DataManager.create_event(request.form, imd)
            if event:
                return redirect(url_for('.details_view', event_id=event.id))
            return redirect(url_for('.index_view'))
        return self.render('/gentelella/admin/event/new/new.html',
                           start_date=datetime.datetime.now() + datetime.timedelta(days=10),
                           event_types=DataGetter.get_event_types(),
                           event_topics=DataGetter.get_event_topics())

    @expose('/<int:event_id>/', methods=('GET', 'POST'))
    def details_view(self, event_id):
        event = DataGetter.get_event(event_id)

        checklist = {"": ""}

        if fields_not_empty(event, ['name', 'start_time', 'end_time', 'location_name', 'organizer_name', 'organizer_description']):
            checklist["1"] = 'success'
        elif fields_not_empty(event, ['name', 'start_time', 'end_time']):
            checklist["1"] = 'missing_some'
        else:
            checklist["1"] = 'missing_main'

        call_for_speakers = DataGetter.get_call_for_papers(event_id).first()
        if call_for_speakers:
            if fields_not_empty(call_for_speakers, ['announcement', 'start_date', 'end_date']):
                checklist["4"] = "success"
            elif fields_not_empty(call_for_speakers, ['start_date', 'end_date']):
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
        return self.render('/gentelella/admin/event/details/details.html', event=event, checklist=checklist)

    @expose('/<int:event_id>/edit/', methods=('GET', 'POST'))
    @is_organizer
    def edit_view(self, event_id):
        event = DataGetter.get_event(event_id)
        session_types = DataGetter.get_session_types_by_event_id(event_id).all()
        tracks = DataGetter.get_tracks(event_id).all()
        social_links = DataGetter.get_social_links_by_event_id(event_id)
        microlocations = DataGetter.get_microlocations(event_id).all()
        call_for_speakers = DataGetter.get_call_for_papers(event_id).first()
        sponsors = DataGetter.get_sponsors(event_id)

        if request.method == 'GET':
            return self.render('/gentelella/admin/event/edit/edit.html', event=event, session_types=session_types,
                               tracks=tracks, social_links=social_links, microlocations=microlocations,
                               call_for_speakers=call_for_speakers, sponsors=sponsors, event_types=DataGetter.get_event_types(),
                               event_topics=DataGetter.get_event_topics())
        if request.method == "POST":
            event = DataManager.edit_event(request, event_id, event, session_types, tracks, social_links,
                                           microlocations, call_for_speakers, sponsors)
            return redirect(url_for('.details_view', event_id=event_id))

    @expose('/<int:event_id>/delete/', methods=('GET',))
    def delete_view(self, event_id):
        if request.method == "GET":
            DataManager.delete_event(event_id)
        return redirect(url_for('.index_view'))

    @expose('/<int:event_id>/update/', methods=('POST',))
    def save_closing_date(self, event_id):
        event = DataGetter.get_event(event_id)
        event.closing_datetime = request.form['closing_datetime']
        save_to_db(event, 'Closing Datetime Updated')
        return self.render('/gentelella/admin/event/details/details.html', event=event)
