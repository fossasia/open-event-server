from flask import request
from flask_admin import expose
from super_admin_base import SuperAdminBaseView, SETTINGS

from app.settings import get_settings, set_settings
from app.helpers.data_getter import DataGetter
from werkzeug.datastructures import ImmutableMultiDict
from app.views.admin.models_views.events import EventsView

class SuperAdminSettingsView(SuperAdminBaseView):
    PANEL_NAME = SETTINGS

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        if request.method == 'POST':
            if 'service_fee' in request.form:
                dic = ImmutableMultiDict(request.form)
            else:
                dic = dict(request.form.copy())
                for i in dic:
                    v = dic[i][0]
                    if not v:
                        dic[i] = None
                    else:
                        dic[i] = v
            set_settings(**dic)

        settings = get_settings()
        fees = DataGetter.get_fee_settings()
        event_view = EventsView()

        return self.render(
            '/gentelella/admin/super_admin/settings/settings.html',
            settings=settings,
            fees=fees,
            payment_currencies=DataGetter.get_payment_currencies(),
            included_settings=event_view.get_module_settings()
        )

    # @expose('/update', methods=('POST'))
    # def update_view(self):
    #     print request.form
    #     # set_settings(request.form[])
