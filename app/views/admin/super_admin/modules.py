from flask_admin import expose
from flask import request
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from app.models.modules import Module
from app.helpers.data import  save_to_db
from app.helpers.data_getter import DataGetter


class SuperAdminModulesView(SuperAdminBaseView):
    @expose('/', methods=['GET', 'POST'])
    def index_view(self):
        module = DataGetter.get_module()
        if request.method == 'GET':
            if not module:
                module = Module()
                save_to_db(module)
        elif request.method == 'POST':
            form = request.form
            module.ticket_include = True if form.get('ticketing') == 'on' else False
            module.payment_include = True if form.get('payments') == 'on' else False
            module.donation_include = True if form.get('donations') == 'on' else False
            save_to_db(module)

        return self.render('/gentelella/admin/super_admin/modules/modules.html',
            module=module)
