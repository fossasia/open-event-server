from flask import render_template
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS, generate_hash
from app.models.badge_field_form import BadgeFieldForms


def file_pdf_path(self) -> str:
    key = UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=self.badge_id)
    return f'static/media/{key}/{generate_hash(key)}/{self.badge_id}.pdf'


def create_preivew_badge_pdf(badgeForms):
    """
    Create tickets and invoices for the holders of an order.
    :param badgeForms: The order for which to create tickets for.
    """
    badgeFieldForms = badgeForms['badgeFields']
    badgeId = badgeForms['badgeID']
    create_save_pdf(
        render_template(
            'pdf/badge_forms.html', badgeForms=badgeForms, badgeFieldForms=badgeFieldForms
        ),
        UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeId),
        identifier=badgeId,
    )
    key = UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeId)
    return f'static/media/{key}/{generate_hash(key)}/{badgeId}.pdf'


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
            field.sample_text = getattr(ticketHolder, field.field_identifier)
        except AttributeError:
            try:
                field.sample_text = ticketHolder.complex_field_values[
                    field.field_identifier
                ]
            except AttributeError:
                raise ObjectNotFound(
                    {'parameter': '{field.field_identifier}'}, "Access Code:  not found"
                )

    create_save_pdf(
        render_template(
            'pdf/badge_forms.html', badgeForms=badgeForms, badgeFieldForms=badgeFieldForms
        ),
        UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeForms.badge_id),
        identifier=badgeForms.badge_id,
    )
    return file_pdf_path(badgeForms)
