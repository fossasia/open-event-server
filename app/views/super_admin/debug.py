import flask_login
from flask import Blueprint
from flask import render_template
from flask import request

from app.helpers.flask_helpers import get_real_ip
from app.views.super_admin import check_accessible, list_navbar, BASE

sadmin_debug = Blueprint('sadmin_debug', __name__, url_prefix='/admin/debug')


@sadmin_debug.before_request
def verify_accessible():
    return check_accessible(BASE)


@sadmin_debug.route('/')
@flask_login.login_required
def display_debug_info():
    return render_template('gentelella/admin/super_admin/debug/debug.html',
                           ip=get_real_ip(),
                           cookies=request.cookies,
                           navigation_bar=list_navbar(),
                           headers=request.headers)

