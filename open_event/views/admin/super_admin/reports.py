import os

from flask import request, url_for, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask.ext import login
from ....helpers.data_getter import DataGetter
from flask_admin import BaseView


class SuperAdminReportsView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))

    @expose('/')
    def index_view(self):
        return self.render('/gentelella/admin/super_admin/reports/reports.html')
