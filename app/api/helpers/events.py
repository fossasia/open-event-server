from app.api.helpers.db import save_to_db
from app.api.helpers.utilities import to_snake_case
from app.models.custom_form import (
    CustomForms,
    ATTENDEE_FORM,
    SPEAKER_FORM,
    SESSION_FORM,
    CUSTOM_FORM_IDENTIFIER_NAME_MAP,
)


def create_custom_forms_for_attendees(event):
    """
    Create and save the custom forms for the required fields of attendees.
    :param event:
    :return:
    """
    # common values
    form = 'attendee'
    event_id = event.id
    form_dict = CUSTOM_FORM_IDENTIFIER_NAME_MAP[form]

    for x in form_dict:
        form_type = 'email' if x == 'email' else 'text'

        is_required = bool(ATTENDEE_FORM[to_snake_case(x)]['require'])
        is_included = bool(ATTENDEE_FORM[to_snake_case(x)]['include'])

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

    form_dict = CUSTOM_FORM_IDENTIFIER_NAME_MAP[form]
    for x in form_dict:
        form_type = 'email' if x == 'email' else 'text'

        is_required = bool(SPEAKER_FORM[to_snake_case(x)]['require'])
        is_included = bool(SPEAKER_FORM[to_snake_case(x)]['include'])

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
        is_required = bool(SESSION_FORM[to_snake_case(x)]['require'])
        is_included = bool(SESSION_FORM[to_snake_case(x)]['include'])

        form_name = CustomForms(
            form=form,
            event_id=event_id,
            type=form_type,
            is_required=is_required,
            is_included=is_included,
            field_identifier=x,
        )
        save_to_db(form_name, x.upper() + 'Form saved')
