from app.api.helpers.db import save_to_db
from app.models.custom_form import CUSTOM_FORM_IDENTIFIER_NAME_MAP, CustomForms


def create_custom_forms_for_attendees(event):
    """
    Create and save the custom forms for the required fields of attendees.
    :param event:
    :return:
    """
    # common values
    form = 'attendee'
    event_id = event.id
    form_type = 'text'
    is_required = False
    is_included = False

    form_dict = CUSTOM_FORM_IDENTIFIER_NAME_MAP[form]
    for x in form_dict:
        form_name = x + "_form"
        form_type = 'email' if x == 'email' else 'text'

        is_required = True if x in ['firstname', 'lastname', 'email'] else False
        is_included = (
            True
            if x
            in [
                'firstname',
                'lastname',
                'email',
                'address',
                'city',
                'state',
                'country',
                'jobTitle',
                'phone',
                'taxBusinessInfo',
                'company',
                'website',
                'twitter',
                'github',
            ]
            else False
        )

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
            is_required=is_required,
            is_included=is_included,
            field_identifier=x,
        )
        save_to_db(form_name, x.upper() + 'Form saved')


def create_custom_forms_for_speakers(event):
    """
    Create and save the custom forms for the required fields of speakers.
    :param event:
    :return:
    """
    # common values
    form = 'speaker'
    event_id = event.id
    form_type = 'text'

    form_dict = CUSTOM_FORM_IDENTIFIER_NAME_MAP[form]
    for x in form_dict:
        form_name = x + "_form"
        form_type = 'email' if x == 'email' else 'text'

        is_required = True if x in ['name', 'email'] else False
        is_included = (
            True
            if x
            in [
                'name',
                'email',
                'photoUrl',
                'organisation',
                'position',
                'country',
                'shortBiography',
                'website',
                'twitter',
            ]
            else False
        )

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
            is_required=is_required,
            is_included=is_included,
            field_identifier=x,
        )
        save_to_db(form_name, x.upper() + 'Form saved')


def create_custom_forms_for_sessions(event):
    """
    Create and save the custom forms for the required fields of sessions.
    :param event:
    :return:
    """
    # common values
    form = 'session'
    event_id = event.id
    form_type = 'text'

    form_dict = CUSTOM_FORM_IDENTIFIER_NAME_MAP[form]
    for x in form_dict:
        form_name = x + "_form"

        is_required = True if x in ['title'] else False
        is_included = (
            True if x in ['title', 'shortAbstract', 'comments', 'slidesUrl'] else False
        )

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
            is_required=is_required,
            is_included=is_included,
            field_identifier=x,
        )
        save_to_db(form_name, x.upper() + 'Form saved')
