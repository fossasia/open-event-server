import boto
from flask import Blueprint
from flask import render_template
from flask import request, current_app
from werkzeug.datastructures import ImmutableMultiDict

from app.helpers.data import save_to_db, delete_from_db
from app.helpers.data_getter import DataGetter
from app.models.image_sizes import ImageSizes
from app.models.setting import Environment
from app.settings import get_settings, set_settings
from app.views.super_admin import SETTINGS, check_accessible, list_navbar
from app.views.users.events import get_module_settings

sadmin_settings = Blueprint('sadmin_settings', __name__, url_prefix='/admin/settings')


@sadmin_settings.before_request
def verify_accessible():
    return check_accessible(SETTINGS)


@sadmin_settings.route('/', methods=('GET', 'POST'))
def index_view():
    if request.method == 'POST':
        if 'super_admin_email' in request.form:
            super_admin = DataGetter.get_super_admin_user()
            super_admin.email = request.form['super_admin_email']
            save_to_db(super_admin)
        if 'event-thumbnail_width' in request.form:
            im_size_profile = DataGetter.get_image_sizes_by_type(type='profile')
            im_size_event = DataGetter.get_image_sizes_by_type(type='event')
            if im_size_profile and im_size_event:
                im_size_profile.full_width = request.form['profile-large_width']
                im_size_profile.full_height = request.form['profile-large_width']
                im_size_profile.full_aspect = request.form.get('profile-large_aspect', 'off')
                im_size_profile.full_quality = request.form['profile-large_quality']
                im_size_profile.icon_width = request.form['profile-icon_width']
                im_size_profile.icon_height = request.form['profile-icon_width']
                im_size_profile.icon_aspect = request.form.get('profile-icon_aspect', 'off')
                im_size_profile.icon_quality = request.form['profile-icon_quality']
                im_size_profile.thumbnail_width = request.form['profile-thumbnail_width']
                im_size_profile.thumbnail_height = request.form['profile-thumbnail_width']
                im_size_profile.thumbnail_aspect = request.form.get('profile-thumbnail_aspect', 'off')
                im_size_profile.thumbnail_quality = request.form['profile-thumbnail_quality']
                im_size_profile.logo_width = None
                im_size_profile.logo_height = None
                save_to_db(im_size_profile, "Image Sizes saved")
                im_size_event.full_width = request.form['event-large_width']
                im_size_event.full_height = request.form['event-large_height']
                im_size_event.full_aspect = request.form.get('event-large_aspect', 'off')
                im_size_event.full_quality = request.form['event-large_quality']
                im_size_event.icon_width = request.form['event-icon_width']
                im_size_event.icon_height = request.form['event-icon_height']
                im_size_event.icon_aspect = request.form.get('event-icon_aspect', 'off')
                im_size_event.icon_quality = request.form['event-icon_quality']
                im_size_event.thumbnail_width = request.form['event-thumbnail_width']
                im_size_event.thumbnail_height = request.form['event-thumbnail_height']
                im_size_event.thumbnail_aspect = request.form.get('event-thumbnail_aspect', 'off')
                im_size_event.thumbnail_quality = request.form['event-thumbnail_quality']
                im_size_event.logo_width = request.form['logo_width']
                im_size_event.logo_height = request.form['logo_height']
                save_to_db(im_size_event, "Image Sizes saved")
            else:
                all_im_sizes = DataGetter.get_image_sizes()
                for sizes in all_im_sizes:
                    delete_from_db(sizes, 'Delete Image Sizes')

                im_size = ImageSizes(type='profile',
                                     full_width=request.form['profile-large_width'],
                                     full_height=request.form['profile-large_width'],
                                     full_aspect=request.form.get('profile-large_aspect', 'off'),
                                     full_quality=request.form['profile-large_quality'],
                                     icon_width=request.form['profile-icon_width'],
                                     icon_height=request.form['profile-icon_width'],
                                     icon_aspect=request.form.get('profile-icon_aspect', 'off'),
                                     icon_quality=request.form['profile-icon_quality'],
                                     thumbnail_width=request.form['profile-thumbnail_width'],
                                     thumbnail_height=request.form['profile-thumbnail_width'],
                                     thumbnail_aspect=request.form.get('profile-thumbnail_aspect', 'off'),
                                     thumbnail_quality=request.form['profile-thumbnail_quality'],
                                     logo_width=None,
                                     logo_height=None)
                save_to_db(im_size, "Image Sizes saved")
                im_size = ImageSizes(type='event',
                                     full_width=request.form['event-large_width'],
                                     full_height=request.form['event-large_height'],
                                     full_aspect=request.form.get('event-large_aspect', 'off'),
                                     full_quality=request.form['profile-large_quality'],
                                     icon_width=request.form['event-icon_width'],
                                     icon_height=request.form['event-icon_height'],
                                     icon_aspect=request.form.get('event-icon_aspect', 'off'),
                                     icon_quality=request.form['profile-icon_quality'],
                                     thumbnail_width=request.form['event-thumbnail_width'],
                                     thumbnail_height=request.form['event-thumbnail_height'],
                                     thumbnail_aspect=request.form.get('event-thumbnail_aspect', 'off'),
                                     thumbnail_quality=request.form['profile-thumbnail_quality'],
                                     logo_width=request.form['logo_width'],
                                     logo_height=request.form['logo_height'])
                save_to_db(im_size, "Image Sizes saved")

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
    image_config = DataGetter.get_image_configs()
    event_image_sizes = DataGetter.get_image_sizes_by_type(type='event')
    profile_image_sizes = DataGetter.get_image_sizes_by_type(type='profile')

    if current_app.config['PRODUCTION']:
        settings['app_environment'] = Environment.PRODUCTION
    elif current_app.config['STAGING']:
        settings['app_environment'] = Environment.STAGING
    elif current_app.config['DEVELOPMENT']:
        settings['app_environment'] = Environment.DEVELOPMENT

    return render_template(
        'gentelella/super_admin/settings/settings.html',
        settings=settings,
        fees=fees,
        s3_regions=boto.s3.regions(),
        payment_currencies=DataGetter.get_payment_currencies(),
        included_settings=get_module_settings(),
        image_config=image_config,
        super_admin_email=DataGetter.get_super_admin_user().email,
        event_image_sizes=event_image_sizes,
        profile_image_sizes=profile_image_sizes,
        navigation_bar=list_navbar()
    )
