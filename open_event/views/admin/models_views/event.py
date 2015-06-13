"""Written by - Rafal Kowalski"""
from flask import request, url_for, redirect

from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater
from flask.ext.admin import expose
from ....models.track import Track
from ....models.event import Event
from ....models.session import Session
from ....models.speaker import Speaker
from ....models.sponsor import Sponsor
from ....models.microlocation import Microlocation
from ....models import db
from flask import flash
from ....helpers.query_filter import QueryFilter
from open_event.forms.admin.session_form import SessionForm
from open_event.forms.admin.speaker_form import SpeakerForm
from open_event.forms.admin.sponsor_form import SponsorForm
from sqlalchemy.orm.collections import InstrumentedList
from ....helpers.data import DataManager

class EventView(ModelView):

    column_list = ('id',
                   'name',
                   'email',
                   'color',
                   'logo',
                   'start_time',
                   'end_time',
                   'latitude',
                   'longitude',
                   'location_name')

    column_formatters = {
        'name': Formatter.column_formatter,
        'location_name': Formatter.column_formatter,
        'logo': Formatter.column_formatter
    }

    def on_model_change(self, form, model, is_created):
        v = VersionUpdater(event_id=model.id, is_created=is_created, column_to_increment="event_ver")
        v.update()

    @expose('/<event_id>')
    def event(self, event_id):
        events = Event.query.all()
        return self.render('admin/model/track/list1.html', event_id=event_id, events=events)

    @expose('/<event_id>/track')
    def event_tracks(self, event_id):
        tracks = Track.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/track/list1.html', objects=tracks, event_id=event_id, events=events)

    @expose('/<event_id>/track/new', methods=('GET', 'POST'))
    def event_track_new(self, event_id):
        events = Event.query.all()
        from open_event.forms.admin.track_form import TrackForm
        form = TrackForm(request.form)
        if form.validate():
            DataManager.create_track(form, event_id)
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/track/create1.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/track/<track_id>/edit', methods=('GET', 'POST'))
    def event_track_edit(self, event_id, track_id):
        track = Track.query.get(track_id)
        events = Event.query.all()
        from open_event.forms.admin.track_form import TrackForm
        print "Test", track.session
        form = TrackForm(obj=track)
        if form.validate():
            DataManager.update_track(form, track)
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/track/<track_id>/delete', methods=('GET', 'POST'))
    def event_track_delete(self, event_id, track_id):
        DataManager.remove_track(track_id)
        return redirect(url_for('.event_tracks', event_id=event_id))

    @expose('/<event_id>/session')
    def event_sessions(self, event_id):
        sessions = Session.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/session/list.html', objects=sessions, event_id=event_id, events=events)

    @expose('/<event_id>/session/new', methods=('GET', 'POST'))
    def event_session_new(self, event_id):
        events = Event.query.all()
        form = SessionForm()
        if form.validate():
            DataManager.create_session(form, event_id)
            return redirect(url_for('.event_sessions', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/session/<session_id>/edit', methods=('GET', 'POST'))
    def event_session_edit(self, event_id, session_id):
        session = Session.query.get(session_id)
        events = Event.query.all()
        form = SessionForm(obj=session)
        if form.validate():
            DataManager.update_session(form, session)
            return redirect(url_for('.event_sessions', event_id=event_id))
        return self.render('admin/model/session/create.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/session/<session_id>/delete', methods=('GET', 'POST'))
    def event_session_delete(self, event_id, session_id):
        DataManager.remove_track(session_id)
        return redirect(url_for('.event_sessions', event_id=event_id))

    @expose('/<event_id>/speaker')
    def event_speakers(self, event_id):
        speakers = Speaker.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/speaker/list.html', objects=speakers, event_id=event_id, events=events)

    @expose('/<event_id>/speaker/new', methods=('GET', 'POST'))
    def event_speaker_new(self, event_id):
        events = Event.query.all()
        form = SpeakerForm()
        if form.validate():
            DataManager.create_speaker(form, event_id)
            return redirect(url_for('.event_speakers', event_id=event_id))
        return self.render('admin/model/speaker/create.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/speaker/<speaker_id>/edit', methods=('GET', 'POST'))
    def event_speaker_edit(self, event_id, speaker_id):
        speaker = Speaker.query.get(speaker_id)
        events = Event.query.all()
        form = SpeakerForm(obj=speaker)
        if form.validate():
            DataManager.create_speaker(form, event_id)
            return redirect(url_for('.event_speakers', event_id=event_id))
        return self.render('admin/model/speaker/create.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/speaker/<speaker_id>/delete', methods=('GET', 'POST'))
    def event_speaker_delete(self, event_id, speaker_id):
        DataManager.remove_speaker(speaker_id)
        return redirect(url_for('.event_speakers', event_id=event_id))

    @expose('/<event_id>/sponsor')
    def event_sponsors(self, event_id):
        sponsors = Sponsor.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/sponsor/list.html', objects=sponsors, event_id=event_id, events=events)

    @expose('/<event_id>/sponsor/new', methods=('GET', 'POST'))
    def event_sponsor_new(self, event_id):
        events = Event.query.all()
        form = SponsorForm()
        if form.validate():
            DataManager.create_sponsor(form, event_id)
            return redirect(url_for('.event_sponsors', event_id=event_id))
        return self.render('admin/model/sponsor/create.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/sponsor/<sponsor_id>/edit', methods=('GET', 'POST'))
    def event_sponsor_edit(self, event_id, sponsor_id):
        sponsor = Sponsor.query.get(sponsor_id)
        events = Event.query.all()
        form = SponsorForm(obj=sponsor)
        if form.validate():
            DataManager.create_sponsor(form, event_id)
            return redirect(url_for('.event_sponsors', event_id=event_id))
        return self.render('admin/model/sponsor/create.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/sponsor/<sponsor_id>/delete', methods=('GET', 'POST'))
    def event_sponsor_delete(self, event_id, sponsor_id):
        DataManager.remove_sponsor(sponsor_id)
        return redirect(url_for('.event_sponsors', event_id=event_id))

    @expose('/<event_id>/microlocation')
    def event_microlocations(self, event_id):
        microlocations = Microlocation.query.filter_by(event_id=event_id)
        events = Event.query.all()
        return self.render('admin/model/microlocation/list.html', objects=microlocations, event_id=event_id, events=events)

    @expose('/<event_id>/microlocation/new', methods=('GET', 'POST'))
    def event_microlocation_new(self, event_id):
        events = Event.query.all()
        from open_event.forms.admin.microlocation_form import MicrolocationForm
        form = MicrolocationForm()
        if form.validate():
            DataManager.create_microlocation(form, event_id)
            return redirect(url_for('.event_microlocations', event_id=event_id))
        return self.render('admin/model/microlocation/create.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/microlocation/<microlocation_id>/edit', methods=('GET', 'POST'))
    def event_microlocation_edit(self, event_id, microlocation_id):
        microlocation = Microlocation.query.get(microlocation_id)
        events = Event.query.all()
        from open_event.forms.admin.microlocation_form import MicrolocationForm
        form = MicrolocationForm(obj=microlocation)
        if form.validate():
            DataManager.create_microlocation(form, event_id)
            return redirect(url_for('.event_microlocations', event_id=event_id))
        return self.render('admin/model/microlocation/create.html', form=form, event_id=event_id, events=events)

    @expose('/<event_id>/microlocation/<microlocation_id>/delete', methods=('GET', 'POST'))
    def event_microlocation_delete(self, event_id, microlocation_id):
        DataManager.remove_microlocation(microlocation_id)
        return redirect(url_for('.event_microlocations', event_id=event_id))