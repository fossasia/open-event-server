from flask import request, url_for, redirect
from flask.ext.restplus import abort
from flask_admin import BaseView
from flask.ext import login

class SuperAdminBaseView(BaseView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login_view', next=request.url))
        else:
            if not login.current_user.is_staff:
                abort(403)
