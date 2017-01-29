from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash

from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.models.modules import Module
from app.views.super_admin import MODULES, check_accessible, list_navbar

sadmin_modules = Blueprint('sadmin_modules', __name__, url_prefix='/admin/modules')


@sadmin_modules.before_request
def verify_accessible():
    return check_accessible(MODULES)


@sadmin_modules.route('/', methods=['GET', 'POST'])
def index_view():
    module = DataGetter.get_module()
    if request.method == 'GET':
        if not module:
            module = Module()
            save_to_db(module)
            flash("Changes have been saved.")
    elif request.method == 'POST':
        form = request.form
        module.ticket_include = True if form.get('ticketing') == 'on' else False
        module.payment_include = True if form.get('payments') == 'on' else False
        module.donation_include = True if form.get('donations') == 'on' else False
        save_to_db(module)
        flash("Changes have been saved.")

    return render_template('gentelella/super_admin/modules/modules.html', module=module, navigation_bar=list_navbar())
