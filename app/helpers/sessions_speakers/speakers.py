from app.helpers.assets.images import save_resized_image, get_path_of_temp_url, save_event_image
from app.helpers.data_getter import DataGetter
from app.helpers.storage import UPLOAD_PATHS
from app.models.image_sizes import ImageSizes
from app.models.speaker import Speaker


def speaker_image_sizes():
    image_sizes = DataGetter.get_image_sizes_by_type(type='profile')
    if not image_sizes:
        image_sizes = ImageSizes(full_width=150,
                                 full_height=150,
                                 full_aspect='on',
                                 icon_width=35,
                                 icon_height=35,
                                 icon_aspect='on',
                                 thumbnail_width=50,
                                 thumbnail_height=50,
                                 thumbnail_aspect='on',
                                 type='profile')
        from app.helpers.data import save_to_db
        save_to_db(image_sizes, "Image Sizes Saved")
    return image_sizes


def trim_get_form(form, key, default=None):
    value = form.get(key, default)
    if not value:
        return value

    return value.strip()


def save_speaker(request, event_id=None, speaker=None, user=None):
    if not speaker and not event_id:
        raise Exception('event_id or speaker is required')

    from app.helpers.data import save_to_db, record_activity

    if not speaker:
        speaker = Speaker(
            event_id=event_id,
            user=user,
            name=trim_get_form(request.form, 'name', None),
            email=trim_get_form(request.form, 'email', None)
        )
        save_to_db(speaker)

    speaker.email = trim_get_form(request.form, 'email', None)
    if trim_get_form(request.form, 'name', None):
        speaker.name = trim_get_form(request.form, 'name', None)

    if not speaker.user:
        if user:
            speaker.user = user
        else:
            speaker.user = DataGetter.get_or_create_user_by_email(speaker.email, {
                'firstname': speaker.name,
                'lastname': ''
            })

    if not event_id:
        event_id = speaker.event_id

    image_sizes = speaker_image_sizes()

    photo = trim_get_form(request.form, 'photo', None)
    if photo and photo.strip() != '':
        if speaker.photo != photo:
            file_path = get_path_of_temp_url(photo)
            speaker.photo = save_untouched_photo(photo, event_id, speaker.id)
            speaker.small = save_resized_photo(file_path, event_id, speaker.id, 'small', image_sizes)
            speaker.thumbnail = save_resized_photo(file_path, event_id, speaker.id, 'thumbnail', image_sizes)
            speaker.icon = save_resized_photo(file_path, event_id, speaker.id, 'icon', image_sizes)
    else:
        speaker.photo = ''
        speaker.small = ''
        speaker.thumbnail = ''
        speaker.icon = ''

    speaker.short_biography = trim_get_form(request.form, 'short_biography', None)
    speaker.long_biography = trim_get_form(request.form, 'long_biography', None)
    speaker.mobile = trim_get_form(request.form, 'mobile', None)
    speaker.website = trim_get_form(request.form, 'website', None)
    speaker.twitter = trim_get_form(request.form, 'twitter', None)
    speaker.facebook = trim_get_form(request.form, 'facebook', None)
    speaker.github = trim_get_form(request.form, 'github', None)
    speaker.linkedin = trim_get_form(request.form, 'linkedin', None)
    speaker.organisation = trim_get_form(request.form, 'organisation', None)
    speaker.featured = True if trim_get_form(request.form, 'featured', 'false') == 'true' else False
    speaker.position = trim_get_form(request.form, 'position', None)
    speaker.country = trim_get_form(request.form, 'country', None)
    speaker.city = trim_get_form(request.form, 'city', None)
    speaker.gender = trim_get_form(request.form, 'gender', None)
    if trim_get_form(request.form, 'heard_from', None) == "Other":
        speaker.heard_from = trim_get_form(request.form, 'other_text', None)
    else:
        speaker.heard_from = trim_get_form(request.form, 'heard_from', None)
    speaker.sponsorship_required = trim_get_form(request.form, 'sponsorship_required', None)
    speaker.speaking_experience = trim_get_form(request.form, 'speaking_experience', None)
    save_to_db(speaker, "Speaker has been updated")
    record_activity('update_speaker', speaker=speaker, event_id=event_id)
    return speaker


def save_untouched_photo(photo_url, event_id, speaker_id):
    """
    Save the untouched background image
    :param speaker_id:
    :param photo_url:
    :param event_id:
    :return:
    """
    upload_path = UPLOAD_PATHS['speakers']['photo'].format(
        event_id=int(event_id),
        id=int(speaker_id)
    )
    return save_event_image(photo_url, upload_path)


def save_resized_photo(background_image_file, event_id, speaker_id, size, image_sizes):
    """
    Save the resized version of the background image
    :param speaker_id:
    :param background_image_file:
    :param event_id:
    :param size:
    :param image_sizes:
    :return:
    """

    basewidth = image_sizes.full_width
    height_size = image_sizes.full_height

    if size == 'small':
        basewidth = image_sizes.thumbnail_width
        height_size = image_sizes.thumbnail_height
    elif size == 'thumbnail':
        basewidth = image_sizes.full_width
        height_size = image_sizes.full_height
    elif size == 'icon':
        basewidth = image_sizes.icon_width
        height_size = image_sizes.icon_height

    upload_path = UPLOAD_PATHS['speakers'][size].format(
        event_id=int(event_id), id=int(speaker_id)
    )

    if basewidth != height_size:
        if height_size > basewidth:
            basewidth = height_size
        else:
            height_size = basewidth

    return save_resized_image(background_image_file, basewidth, 'off', height_size, upload_path)
