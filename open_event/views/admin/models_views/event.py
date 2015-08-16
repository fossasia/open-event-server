"""Copyright 2015 Rafal Kowalski"""
from flask import request, url_for, redirect, flash
from flask.ext import login
from sqlalchemy.exc import IntegrityError
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin import expose
from flask_admin.helpers import get_redirect_target

from open_event.forms.admin.session_form import SessionForm
from open_event.forms.admin.speaker_form import SpeakerForm
from open_event.forms.admin.sponsor_form import SponsorForm
from open_event.forms.admin.track_form import TrackForm
from open_event.forms.admin.microlocation_form import MicrolocationForm
from open_event.forms.admin.level_form import LevelForm
from open_event.forms.admin.format_form import FormatForm

from ....helpers.data import DataManager, save_to_db, delete_from_db
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater
from ....helpers.helpers import is_track_name_unique_in_event, is_event_admin
from ....helpers.data_getter import DataGetter
from ....forms.admin.file_form import FileForm

class EventView(ModelView):
    form = None
    column_list = ('id',
                   'name',
                   'email',
                   'color',
                   'logo',
                   'start_time',
                   'end_time',
                   'latitude',
                   'longitude',
                   'location_name',
                   'slogan',
                   'url')

    column_formatters = {
        'name': Formatter.column_formatter,
        'location_name': Formatter.column_formatter,
        'logo': Formatter.column_formatter
    }

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    def on_model_change(self, form, model, is_created):
        v = VersionUpdater(event_id=model.id,
                           is_created=is_created,
                           column_to_increment="event_ver")
        v.update()
        if is_created:
            owner_id = login.current_user.id
            DataManager.add_owner_to_event(owner_id, model)

    @expose('/')
    def index_view(self):
        self._template_args['events'] = DataGetter.get_all_events()
        self.name = "Event"
        return super(EventView, self).index_view()

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        events = DataGetter.get_all_events()
        self._template_args['return_url'] = get_redirect_target() or self.get_url('.index_view')
        self.name = "Event | New"
        from ....forms.admin.event_form import EventForm
        self.form = EventForm()
        self.form.logo.choices=DataGetter.get_all_files_tuple()
        self.form.logo.choices.insert(0, ('', ''))
        if self.form.validate():
            if request.method == "POST":
                DataManager.create_event(self.form)
                flash("Event updated")
                return redirect(url_for('.index_view'))
        return self.render('admin/model/create_model.html',
                           form=self.form,
                           events=events,
                           cancel_url=url_for('.index_view'))

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        events = DataGetter.get_all_events()
        event_id = get_mdict_item_or_list(request.args, 'id')
        self.name = "Event | Edit"
        event = DataGetter.get_event(event_id)
        from ....forms.admin.event_form import EventForm
        self.form = EventForm(obj=event)
        self.form.logo.choices=DataGetter.get_all_files_tuple()
        self.form.logo.choices.insert(0, ('', ''))
        if self.form.validate():
            if request.method == "POST":
                if is_event_admin_or_editor(event_id):
                    DataManager.update_event(self.form, event)
                    flash("Event updated")
                else:
                    flash("You don't have permission!")
                return redirect(url_for('.index_view', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=self.form,
                           event_id=event_id,
                           events=events,
                           # owner=DataGetter.get_event_owner(event_id),
                           cancel_url=url_for('.index_view'))

    @expose('/<event_id>')
    def event(self, event_id):
        events = DataGetter.get_all_events()
        self.name = "Event | " + event_id
        return self.render('admin/base1.html',
                           event_id=event_id,
                           events=events,
                           owner=DataGetter.get_event_owner(event_id))

    @expose('/<event_id>/track')
    def event_tracks(self, event_id):
        tracks = DataGetter.get_tracks(event_id)
        events = DataGetter.get_all_events()
        self.name = "Track"
        return self.render('admin/model/track/list1.html',
                           objects=tracks,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/track/new', methods=('GET', 'POST'))
    def event_track_new(self, event_id):
        events = DataGetter.get_all_events()
        form = TrackForm(request.form)
        self.name = " Track | New"
        if form.validate():
            if is_event_admin_or_editor(event_id) and is_track_name_unique_in_event(form, event_id):
                DataManager.create_track(form, event_id)
                flash("Track added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_tracks', event_id=event_id))

    @expose('/<event_id>/track/<track_id>/edit', methods=('GET', 'POST'))
    def event_track_edit(self, event_id, track_id):
        track = DataGetter.get_track(track_id)
        events = DataGetter.get_all_events()
        form = TrackForm(obj=track)
        self.name = "Track | Edit"
        if form.validate() and is_track_name_unique_in_event(form, event_id, track_id):
            if is_event_admin_or_editor(event_id):
                DataManager.update_track(form, track)
                flash("Track updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_tracks', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_tracks', event_id=event_id))

    @expose('/<event_id>/track/<track_id>/delete', methods=('GET', 'POST'))
    def event_track_delete(self, event_id, track_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_track(track_id)
            flash("Track deleted")
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_tracks',
                                event_id=event_id))

    @expose('/<event_id>/session')
    def event_sessions(self, event_id):
        sessions = DataGetter.get_sessions(event_id)
        events = DataGetter.get_all_events()
        self.name = "Session"
        return self.render('admin/model/session/list.html',
                           objects=sessions,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/session/new', methods=('GET', 'POST'))
    def event_session_new(self, event_id):
        events = DataGetter.get_all_events()
        form = SessionForm()
        self.name = "Session | New"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.create_session(form, event_id)
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_sessions', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_sessions', event_id=event_id))

    @expose('/<event_id>/session/<session_id>/edit', methods=('GET', 'POST'))
    def event_session_edit(self, event_id, session_id):
        session = DataGetter.get_session(session_id)
        events = DataGetter.get_all_events()
        form = SessionForm(obj=session)
        self.name = "Session | Edit"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.update_session(form, session)
                flash("Session updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_sessions', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_sessions', event_id=event_id))

    @expose('/<event_id>/session/<session_id>/delete', methods=('GET', 'POST'))
    def event_session_delete(self, event_id, session_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_session(session_id)
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_sessions',
                                event_id=event_id))

    @expose('/<event_id>/speaker')
    def event_speakers(self, event_id):
        speakers = DataGetter.get_speakers(event_id)
        events = DataGetter.get_all_events()
        self.name = "Speaker"
        return self.render('admin/model/speaker/list.html',
                           objects=speakers,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/speaker/new', methods=('GET', 'POST'))
    def event_speaker_new(self, event_id):
        events = DataGetter.get_all_events()
        form = SpeakerForm()
        self.name = "Speaker | New"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.create_speaker(form, event_id)
                flash("Speaker added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_speakers', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_speakers', event_id=event_id))

    @expose('/<event_id>/speaker/<speaker_id>/edit', methods=('GET', 'POST'))
    def event_speaker_edit(self, event_id, speaker_id):
        speaker = DataGetter.get_speaker(speaker_id)
        events = DataGetter.get_all_events()
        form = SpeakerForm(obj=speaker)
        self.name = "Speaker " + speaker_id + " | Edit"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.update_speaker(form, speaker)
                flash("Speaker updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_speakers',
                                    event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_speakers', event_id=event_id))

    @expose('/<event_id>/speaker/<speaker_id>/delete', methods=('GET', 'POST'))
    def event_speaker_delete(self, event_id, speaker_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_speaker(speaker_id)
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_speakers',
                                event_id=event_id))

    @expose('/<event_id>/sponsor')
    def event_sponsors(self, event_id):
        sponsors = DataGetter.get_sponsors(event_id)
        events = DataGetter.get_all_events()
        self.name = "Sponsor"
        return self.render('admin/model/sponsor/list.html',
                           objects=sponsors,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/sponsor/new', methods=('GET', 'POST'))
    def event_sponsor_new(self, event_id):
        events = DataGetter.get_all_events()
        form = SponsorForm()
        self.name = "Sponsor | New"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.create_sponsor(form, event_id)
                flash("Sponsor added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_sponsors', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_sponsors', event_id=event_id))

    @expose('/<event_id>/sponsor/<sponsor_id>/edit', methods=('GET', 'POST'))
    def event_sponsor_edit(self, event_id, sponsor_id):
        sponsor = DataGetter.get_sponsor(sponsor_id)
        events = DataGetter.get_all_events()
        form = SponsorForm(obj=sponsor)
        self.name = "Sponsor " + sponsor_id + " | Edit"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.update_sponsor(form, sponsor)
                flash("Sponsor updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_sponsors', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_sponsors', event_id=event_id))

    @expose('/<event_id>/sponsor/<sponsor_id>/delete', methods=('GET', 'POST'))
    def event_sponsor_delete(self, event_id, sponsor_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_sponsor(sponsor_id)
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_sponsors',
                                event_id=event_id))

    @expose('/<event_id>/microlocation')
    def event_microlocations(self, event_id):
        microlocations = DataGetter.get_microlocations(event_id)
        events = DataGetter.get_all_events()
        self.name = "Microlocation"
        return self.render('admin/model/microlocation/list.html',
                           objects=microlocations,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/microlocation/new', methods=('GET', 'POST'))
    def event_microlocation_new(self, event_id):
        events = DataGetter.get_all_events()
        form = MicrolocationForm()
        self.name = "Microlocation | New"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.create_microlocation(form, event_id)
                flash("Microlocation added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_microlocations', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_microlocations', event_id=event_id))

    @expose('/<event_id>/microlocation/<microlocation_id>/edit', methods=('GET', 'POST'))
    def event_microlocation_edit(self, event_id, microlocation_id):
        microlocation = DataGetter.get_microlocation(microlocation_id)
        events = DataGetter.get_all_events()
        form = MicrolocationForm(obj=microlocation)
        self.name = "Microlocation " + microlocation_id + " | Edit"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.update_microlocation(form, microlocation)
                flash("Microlocation updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_microlocations', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_microlocations', event_id=event_id))

    @expose('/<event_id>/microlocation/<microlocation_id>/delete', methods=('GET', 'POST'))
    def event_microlocation_delete(self, event_id, microlocation_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_microlocation(microlocation_id)
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_microlocations',
                                event_id=event_id))

    @expose('/upload', methods=['GET', 'POST'])
    def upload(self):
        """Upload a new file."""
        events = DataGetter.get_all_events()
        files = DataGetter.get_all_owner_files()
        self.form = FileForm()
        if request.method == 'POST':
            DataManager.create_file()

        return self.render('admin/model/file/file.html',
                           form=self.form,
                           events=events,
                           files=files)

    @expose('/remove_file/<file_id>', methods=['GET', 'POST'])
    def remove_file(self, file_id):
        """Upload a new file."""
        events = DataGetter.get_all_events()
        files = DataGetter.get_all_owner_files()
        DataManager.remove_file(file_id)

        return self.render('admin/model/file/file.html',
                           form=self.form,
                           events=events,
                           files=files)

    @expose('/<event_id>/api')
    def api(self, event_id):
        events = DataGetter.get_all_events()
        self.name = "Api | " + event_id
        return self.render('admin/api/index.html',
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/level')
    def event_levels(self, event_id):
        levels = DataGetter.get_levels()
        events = DataGetter.get_all_events()
        self.name = "Level"
        return self.render('admin/model/level/list.html',
                           objects=levels,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/level/new', methods=('GET', 'POST'))
    def event_level_new(self, event_id):
        events = DataGetter.get_all_events()
        form = LevelForm()
        self.name = "Level | New"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.create_level(form, event_id)
                flash("Level added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_levels', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_levels', event_id=event_id))

    @expose('/<event_id>/level/<level_id>/edit', methods=('GET', 'POST'))
    def event_level_edit(self, event_id, level_id):
        level = DataGetter.get_level(level_id)
        events = DataGetter.get_all_events()
        form = LevelForm(obj=level)
        self.name = "Level " + level_id + " | Edit"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.update_level(form, level, event_id)
                flash("Level updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_levels', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_levels', event_id=event_id))

    @expose('/<event_id>/level/<level_id>/delete', methods=('GET', 'POST'))
    def event_level_delete(self, event_id, level_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_level(level_id)
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_levels',
                                event_id=event_id))

    @expose('/<event_id>/format')
    def event_formats(self, event_id):
        formats = DataGetter.get_formats()
        events = DataGetter.get_all_events()
        self.name = "Format"
        return self.render('admin/model/format/list.html',
                           objects=formats,
                           event_id=event_id,
                           events=events)

    @expose('/<event_id>/format/new', methods=('GET', 'POST'))
    def event_format_new(self, event_id):
        events = DataGetter.get_all_events()
        form = FormatForm()
        self.name = "Format | New"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.create_format(form, event_id)
                flash("Format added")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_formats', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_formats', event_id=event_id))

    @expose('/<event_id>/format/<format_id>/edit', methods=('GET', 'POST'))
    def event_format_edit(self, event_id, format_id):
        format = DataGetter.get_format(format_id)
        events = DataGetter.get_all_events()
        form = FormatForm(obj=format)
        self.name = "format " + format_id + " | Edit"
        if form.validate():
            if is_event_admin_or_editor(event_id):
                DataManager.update_format(form, format, event_id)
                flash("Format updated")
            else:
                flash("You don't have permission!")
            return redirect(url_for('.event_formats', event_id=event_id))
        return self.render('admin/model/create_model.html',
                           form=form,
                           event_id=event_id,
                           events=events,
                           cancel_url=url_for('.event_formats', event_id=event_id))

    @expose('/<event_id>/format/<format_id>/delete', methods=('GET', 'POST'))
    def event_format_delete(self, event_id, format_id):
        if is_event_admin_or_editor(event_id):
            DataManager.remove_format(format_id)
        else:
            flash("You don't have permission!")
        return redirect(url_for('.event_formats',
                                event_id=event_id))

    @expose('/<event_id>/user_permissions', methods=('GET', 'POST'))
    def user_permissions(self, event_id):
        users = DataGetter.get_all_users()
        event_users = DataGetter.get_event(event_id).users
        if is_event_admin(event_id, event_users):
            return self.render('admin/permissions/permission.html',
                           event_id=event_id,
                           cancel_url=url_for('.index_view', event_id=event_id),
                           users=users,
                           event_users=event_users)
        else:
            flash("You don't have permission!")
            return redirect(url_for('.index_view',
                                    event_id=event_id))

    @expose('/<event_id>/add_user_to_event', methods=('GET', 'POST'))
    def add_user_to_event(self, event_id):
        event = DataGetter.get_event(event_id)
        for row in request.args.getlist('user'):
            user_id = int(row)
            user = DataGetter.get_user(user_id)
            asso = DataGetter.get_association()
            asso.event_id = event_id
            asso.user = user
            asso.admin = False
            asso.editor = False
            try:
                event.users.append(asso)
                save_to_db(event, "Event updated")
            except Exception:
                pass
        return redirect(url_for('.user_permissions',
                                event_id=event_id))

    @expose('/<event_id>/update_user_permission', methods=('GET', 'POST'))
    def update_user_permission(self, event_id):
        asso = DataGetter.get_association_by_event_and_user(event_id, user_id=int(request.args['id']))
        asso.admin= False
        asso.editor = False
        for arg in request.args:
            if arg == 'admin':
                asso.admin = True
            elif arg == 'editor':
                asso.editor = True
        save_to_db(asso, "Permission updated")
        return redirect(url_for('.user_permissions',
                                event_id=event_id))

    @expose('/<event_id>/delete_user_permission/<user_id>', methods=('GET', 'POST'))
    def delete_user_permission(self, event_id, user_id):
        asso = DataGetter.get_association_by_event_and_user(event_id, user_id=int(user_id))
        delete_from_db(asso, "Permission updated")
        return redirect(url_for('.user_permissions',
                                event_id=event_id))

def is_event_admin_or_editor(event_id):
    asso = DataGetter.get_association_by_event_and_user(event_id, login.current_user.id)
    if asso:
        return asso.admin or asso.editor
    return False