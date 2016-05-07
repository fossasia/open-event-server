from flask_admin import  expose
from flask_admin.contrib.sqla import ModelView
from open_event.forms.admin.track_form import TrackForm
from ...helpers.helpers import is_track_name_unique_in_event
from ...helpers.data_getter import DataGetter
from open_event.models.track import Track
from flask import request, url_for, redirect, flash
from ...helpers.data import DataManager
from flask.ext import login


class TrackView(ModelView):
    @expose('/')
    def index_view(self, event_id):
        """Track list view"""
        tracks = DataGetter.get_tracks(event_id)
        events = DataGetter.get_all_events()
        self.name = "Track"
        return self.render('admin/model/track/list1.html',
                           objects=tracks,
                           event_id=event_id,
                           events=events)

    @expose('/new', methods=('GET', 'POST'))
    def create_view(self, event_id):
        """New track view"""
        events = DataGetter.get_all_events()
        form = TrackForm(request.form)
        self.name = " Track | New"
        if form.validate_on_submit():
            if is_event_admin_or_editor(event_id) and is_track_name_unique_in_event(form, event_id):
                DataManager.create_track(form, event_id)
                flash("Track added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.index_view', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.index_view', event_id=event_id))

    @expose('/edit', methods=('GET', 'POST'))
    def edit_view(self, event_id):
        """Edit track view"""
        track_id = request.args.get('track_id', '')
        track = DataGetter.get_object(Track, track_id)
        events = DataGetter.get_all_events()
        form = TrackForm(obj=track)
        self.name = "Track | Edit"
        if form.validate_on_submit() and is_track_name_unique_in_event(form, event_id, track_id):
            if is_event_admin_or_editor(event_id):
                DataManager.update_track(form, track)
                flash("Track updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.index_view', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.index_view', event_id=event_id))

    @expose('/delete', methods=('GET', 'POST'))
    def delete_view(self, event_id):
        track_id = request.args.get('track_id', '')
        """Delete track method"""
        if is_event_admin_or_editor(event_id):
            DataManager.remove_track(track_id)
            flash("Track deleted")
        else:
            flash("You don't have permission!")
        return redirect(url_for('.index_view',
                                event_id=event_id))


def is_event_admin_or_editor(event_id):
    """check is admin or editor"""
    asso = DataGetter.get_association_by_event_and_user(event_id, login.current_user.id)
    if asso:
        return asso.admin or asso.editor
    return False
