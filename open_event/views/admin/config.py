from flask.ext.admin import BaseView, expose
from open_event.forms.config import ConfigForm
from flask import request, flash

from ...models import db
from ...models.config import Config


class ConfigView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        form = ConfigForm(request.form)
        if request.method == 'POST' and form.validate():
            self._save_settings_to_db(form)
            flash("Settings updated successfully")
            return self.render('admin/config/settings.html', form=form)

        return self.render('admin/config/settings.html', form=self._fill_form(form))

    def _save_settings_to_db(self, form):
        config = Config.query.first()
        if not config:
            # Create new Configuration
            configuration = Config(title=form.title.data,
                                   logo=form.logo.data,
                                   email=form.email.data,
                                   color=str(form.color.data))
            db.session.add(configuration)
        else:
            # Update Configuration
            config.title = form.title.data
            config.logo = form.logo.data
            config.email = form.email.data
            config.color = str(form.color.data)
        db.session.commit()

    def _fill_form(self, form):
        config = Config.query.first()
        if config:
            form.title.data = config.title
            form.email.data = config.email
            form.logo.data = config.logo
            form.color.data = config.color
        return form
