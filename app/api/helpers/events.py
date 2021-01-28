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

    form_dict = CUSTOM_FORM_IDENTIFIER_NAME_MAP[form]
    for x in form_dict:
        form_name = x + "_form"
        if x == 'email':
            form_type = 'email'
        else:
            form_type = 'text'

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
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
        if x == 'email':
            form_type = 'email'
        else:
            form_type = 'text'

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
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
        if x == 'email':
            form_type = 'email'
        else:
            form_type = 'text'

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
            field_identifier=x,
        )
        save_to_db(form_name, x.upper() + 'Form saved')
