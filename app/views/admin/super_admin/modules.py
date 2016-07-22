from flask_admin import expose
from flask import request
from app.views.admin.super_admin.super_admin_base import SuperAdminBaseView
from app.helpers.data import create_modules
from app.helpers.data_getter import DataGetter

class SuperAdminModulesView(SuperAdminBaseView):

    @expose('/')
    def index_view(self):
        module = DataGetter.get_module()
        include_settings = []

        if module:
            if module.ticket_include:
                include_settings.append('ticketing')
            if module.payment_include:
                include_settings.append('payments')
            if module.donation_include:
                include_settings.append('donations')

        return self.render('/gentelella/admin/super_admin/modules/modules.html', include_settings=include_settings)

    @expose('/save', methods=['GET', 'POST'])
    def modules_save_view(self):
        create_modules(request.form)

        include_settings = []
        settings = request.form.getlist('modules_form[value]')

        if settings[0][24] == '1':
            include_settings.append('ticketing')
        if settings[0][49] == '1':
            include_settings.append('payments')
        if settings[0][75] == '1':
            include_settings.append('donations')

        return self.render('/gentelella/admin/super_admin/modules/modules.html', include_settings=include_settings)
