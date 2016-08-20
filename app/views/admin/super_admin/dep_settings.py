from flask import request
from flask_admin import expose
from super_admin_base import SuperAdminBaseView, SETTINGS

from app.settings import get_settings, set_settings
from app.helpers.data_getter import DataGetter
from app.helpers.data import save_to_db
from werkzeug.datastructures import ImmutableMultiDict
from app.views.admin.models_views.events import EventsView
from app.models.image_config import ImageConfig
from app.models.image_sizes import ImageSizes

class SuperAdminSettingsView(SuperAdminBaseView):
    PANEL_NAME = SETTINGS

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        if request.method == 'POST':
            if 'thumbnail_width' in request.form:
                im_size = DataGetter.get_image_sizes()
                if im_size:
                    im_size.full_width = request.form['large_width']
                    im_size.full_height = request.form['large_height']
                    im_size.icon_width = request.form['icon_width']
                    im_size.icon_height = request.form['icon_height']
                    im_size.thumbnail_width = request.form['thumbnail_width']
                    im_size.thumbnail_height = request.form['thumbnail_height']
                else:
                    im_size = ImageSizes(full_width=request.form['large_width'],
                                         full_height=request.form['large_height'],
                                         icon_width=request.form['icon_width'],
                                         icon_height=request.form['icon_width'],
                                         thumbnail_width=request.form['thumbnail_width'],
                                         thumbnail_height=request.form['thumbnail_width'])
                save_to_db(im_size, "Image Sizes saved")
                im_config = DataGetter.get_image_configs()
                if im_config:
                    for config in im_config:
                        config.size = request.form['size_' + config.name]
                        save_to_db(config, "Image Config Saved")
                else:
                    config = ImageConfig(page='front',
                                         size=request.form['size_front'])
                    save_to_db(config, "Image Config Saved")
                    config = ImageConfig(page='mysession',
                                         size=request.form['size_mysession'])
                    save_to_db(config, "Image Config Saved")
                    config = ImageConfig(page='event',
                                         size=request.form['size_event'])
                    save_to_db(config, "Image Config Saved")
                    config = ImageConfig(page='speaker_event',
                                         size=request.form['size_speaker_event'])
                    save_to_db(config, "Image Config Saved")
                    config = ImageConfig(page='speaker_dashboard',
                                         size=request.form['size_speaker_dashboard'])
                    save_to_db(config, "Image Config Saved")

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
