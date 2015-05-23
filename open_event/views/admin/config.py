from flask.ext.admin import BaseView, expose
from open_event.forms.config import ConfigForm
from flask import request

from ...models import db
from ...models.config import Config


class ConfigView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        form = ConfigForm()
        if request.method == 'POST':
            self._save_settings_to_db(request)
            return self.render('admin/config/settings.html', form=form)
        elif request.method == 'GET':

            return self.render('admin/config/settings.html', form=self._fill_form(form))

    def _save_settings_to_db(self, request):
        config = Config.query.first()
        if not config:
            # Create new Configuration
            configuration = Config(title=request.form['title'],
                                   logo=request.form['logo'],
                                   email=request.form['email'],
                                   color=request.form['color'])
            db.session.add(configuration)
            db.session.commit()
        else:
            # Update Configuration
            config.title = request.form['title']
            config.logo = request.form['logo']
            config.email = request.form['email']
            config.color = request.form['color']
            db.session.commit()

    def _fill_form(self, form):
        config = Config.query.first()
        if config:
            form.title.data = config.title
            form.email.data = config.email
            form.logo.data = config.logo
            form.color.data = config.color
        return form



