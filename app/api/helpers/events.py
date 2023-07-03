from app.api.helpers.db import save_to_db
from app.models.custom_form import CustomForms


def create_custom_forms_for_attendees(event):
    """
    Create and save the custom forms for the required fields of attendees.
    :param event:
    :return:
    """
    # common values
    form = 'attendee'
    is_required = True
    is_included = True
    is_fixed = True
    event_id = event.id

    email_form = CustomForms(
        form=form,
        is_required=is_required,
        is_included=is_included,
        is_fixed=is_fixed,
        event_id=event_id,
        type='email',
        field_identifier='email',
    )

    save_to_db(email_form, 'Email form saved')
