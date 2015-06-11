"""Written by - Rafal Kowalski"""
from flask import request, url_for, redirect

from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater
from flask.ext.admin import expose
from ....models.track import Track
from ....models.event import Event
from ....models.session import Session
from ....models import db
from flask import flash
from ....helpers.query_filter import QueryFilter
from open_event.forms.admin.session_form import SessionForm

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
            new_track = Track(name=form.name.data,
                              description=form.description.data,
                              event_id=event_id)
            db.session.add(new_track)
            db.session.commit()
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/track/<track_id>/edit', methods=('GET', 'POST'))
    def event_track_edit(self, event_id, track_id):
        track = Track.query.get(track_id)
        events = Event.query.all()
        from open_event.forms.admin.track_form import TrackForm
        form = TrackForm(obj=track)
        if form.validate():
            track.name = form.name.data
            track.description=form.description.data
            db.session.add(track)
            db.session.commit()
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)

    @expose('/<event_id>/track/<track_id>/delete', methods=('GET', 'POST'))
    def event_track_delete(self, event_id, track_id):
        track = Track.query.get(track_id)
        db.session.delete(track)
        db.session.commit()
        flash('You successfully delete track')
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
        print form.Meta
        print form.validate()
        if form.validate():
            new_session = Session(title=form.title.data,
                                  subtitle=form.subtitle.data,
                                  description=form.description.data,
                                  start_time=form.start_time.data,
                                  end_time=form.end_time.data,
                                  event_id=event_id,
                                  speakers='')
            db.session.add(new_session)
            db.session.commit()
            return redirect(url_for('.event_tracks', event_id=event_id))
        
        return self.render('admin/model/track/create1.html',form=form, event_id=event_id, events=events)
