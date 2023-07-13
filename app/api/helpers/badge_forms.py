from flask import render_template
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS
from app.models.badge_field_form import BadgeFieldForms


def create_preivew_badge_pdf(badgeForms):
    """
    Create tickets and invoices for the holders of an order.
    :param badgeForms: The order for which to create tickets for.
    """
    badgeFieldForms = (
        BadgeFieldForms.query.filter_by(badge_form_id=badgeForms.id)
        .filter_by(badge_id=badgeForms.badge_id)
        .all()
    )
    return create_save_pdf(
        render_template(
            'pdf/badge_forms.html', badgeForms=badgeForms, badgeFieldForms=badgeFieldForms
        ),
        UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeForms.badge_id),
        identifier=badgeForms.badge_id,
    )


def create_print_badge_pdf(badgeForms, ticketHolder):
    """
    Create tickets and invoices for the holders of an order.
    :param badgeForms: The order for which to create tickets for.
    """
    badgeFieldForms = (
        BadgeFieldForms.query.filter_by(badge_form_id=badgeForms.id)
        .filter_by(badge_id=badgeForms.badge_id)
        .all()
    )
    for field in badgeFieldForms:
        try:
            field.sample_text = getattr(ticketHolder, field.custom_field)
        except AttributeError:
            try:
                field.sample_text = ticketHolder.complex_field_values[field.custom_field]
            except AttributeError:
                raise ObjectNotFound(
                    {'parameter': '{field.custom_field}'}, "Access Code:  not found"
                )

    return create_save_pdf(
        render_template(
            'pdf/badge_forms.html', badgeForms=badgeForms, badgeFieldForms=badgeFieldForms
        ),
        UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeForms.badge_id),
        identifier=badgeForms.badge_id,
    )
