from flask import request, redirect, url_for
from flask_admin import expose
from super_admin_base import SuperAdminBaseView
from app.helpers.data import DataManager, save_ticketing_fees
from app.helpers.data_getter import DataGetter


class SuperAdminTicketFeesView(SuperAdminBaseView):
    @expose('/')
    def index_view(self):
        return ''

    @expose('/save', methods=('GET', 'POST'))
    def ticket_fees_save_view(self):
        ticket_fee = save_ticketing_fees(request.form)

        return self.render(
            '/gentelella/admin/super_admin/settings/settings.html',
            fees=ticket_fee,
            payment_currencies=DataGetter.get_payment_currencies(),
        )
