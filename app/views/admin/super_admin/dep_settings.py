from flask import request
from flask_admin import expose
from super_admin_base import SuperAdminBaseView

from app.settings import get_settings, set_settings


class SuperAdminSettingsView(SuperAdminBaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        if request.method == 'POST':
            dic = dict(request.form.copy())
            for i in dic:
                v = dic[i][0]
                if not v:
                    dic[i] = None
                else:
                    dic[i] = v
            set_settings(**dic)

        settings = get_settings()
        return self.render(
            '/gentelella/admin/super_admin/settings/settings.html',
            settings=settings
        )

    # @expose('/update', methods=('POST'))
    # def update_view(self):
    #     print request.form
    #     # set_settings(request.form[])
