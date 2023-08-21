import base64
import io

import qrcode
from flask import render_template

from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS, generate_hash
from app.api.helpers.utilities import to_snake_case
from app.models.badge_field_form import BadgeFieldForms
from app.models.custom_form import CustomForms
from app.models.ticket_holder import TicketHolder


def file_pdf_path(self) -> str:
    """Contructor path of File PDF"""
    key = UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=self.badge_id)
    return f'static/media/{key}/{generate_hash(key)}/{self.badge_id}.pdf'


def create_preivew_badge_pdf(badgeForms):
    """
    Create tickets and invoices for the holders of an order.
    :param badgeForms: The order for which to create tickets for.
    """
    badgeForms = badgeForms[0]
    badgeFieldForms = badgeForms['badgeFields']
    badgeId = badgeForms['badgeID']

    badgeFieldForms = [
        badge_field
        for badge_field in badgeFieldForms
        if badge_field['is_deleted'] is False
    ]

    for badge_field in badgeFieldForms:
        if (
            badge_field.get('custom_field') is not None
            and badge_field.get('custom_field').lower() == 'qr'
        ):
            qr_code_data = get_qr_data_badge_preview(badge_field)
            qr_rendered = render_template('cvf/badge_qr_template.cvf', **qr_code_data)
            badge_field['sample_text'] = create_base64_img_qr(qr_rendered)
            badge_field['text_rotation'] = 0

    for badge_field in badgeFieldForms:
        font_weight = []
        font_style = []
        text_decoration = []
        if badge_field.get('font_weight'):
            for item in badge_field.get('font_weight'):
                if item.get('font_weight'):
                    font_weight.append(item.get('font_weight'))
                if item.get('font_style'):
                    font_style.append(item.get('font_style'))
                if item.get('text_decoration'):
                    text_decoration.append(item.get('text_decoration'))
        if not font_weight:
            badge_field['font_weight'] = 'none'
        else:
            badge_field['font_weight'] = ','.join(font_weight)
        if not font_style:
            badge_field['font_style'] = 'none'
        else:
            badge_field['font_style'] = ','.join(font_style)
        if not text_decoration:
            badge_field['text_decoration'] = 'none'
        else:
            badge_field['text_decoration'] = ','.join(text_decoration)
    create_save_pdf(
        render_template(
            'pdf/badge_forms.html', badgeForms=badgeForms, badgeFieldForms=badgeFieldForms
        ),
        UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeId),
        identifier=badgeId,
        new_renderer=True,
    )
    key = UPLOAD_PATHS['pdf']['badge_forms_pdf'].format(identifier=badgeId)
    return f'static/media/{key}/{generate_hash(key)}/{badgeId}.pdf'


def get_value_from_field_indentifier(field: BadgeFieldForms, ticket_holder: TicketHolder):
    """Get the value of a field."""
    snake_case_field_identifier = to_snake_case(field.field_identifier)
    try:
        field.sample_text = getattr(ticket_holder, snake_case_field_identifier)
    except AttributeError:
        try:
            field.sample_text = ticket_holder.complex_field_values[field.field_identifier]
        except (AttributeError, KeyError):
            print(snake_case_field_identifier)


def get_value_from_qr_filed(field: BadgeFieldForms, ticket_holder: TicketHolder) -> dict:
    """Get the value of a QR code field."""
    qr_value = {}
    custom_fields = []
    if field.qr_custom_field is not None:
        for field_identifier in field.qr_custom_field:
            value_ = ""
            try:
                snake_case_field_identifier = to_snake_case(field_identifier)
                value_ = getattr(ticket_holder, snake_case_field_identifier)
            except AttributeError:
                try:
                    if ticket_holder.complex_field_values is not None:
                        value_ = ticket_holder.complex_field_values[field_identifier]
                        # Get the field description then
                        # Capitalize first letter and remove space.
                        custom_form = CustomForms.query.filter_by(
                            field_identifier=field_identifier,
                            form_id=ticket_holder.ticket.form_id,
                        ).first()
                        field_description = custom_form.description.title().replace(
                            ' ', ''
                        )
                        custom_fields.append({field_description: value_})
                except AttributeError:
                    print(field_identifier)
                except Exception:
                    print(field_identifier)

            qr_value.update({field_identifier: str(value_)})
    qr_value.update({'custom_fields': custom_fields, 'ticket_id': ticket_holder.id})
    return qr_value


def get_qr_data_badge_preview(field: BadgeFieldForms) -> dict:
    """Get the value of a QR code field."""
    qr_value = {}
    if field.get('qr_custom_field') is not None:
        for field_identifier in field.get('qr_custom_field'):
            value_ = "Sample Data"
            qr_value.update({field_identifier: str(value_)})
    return qr_value


def create_base64_img_qr(qr_code_data: str) -> str:
    """Create a base64 image of a QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_code_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    io_buffer = io.BytesIO()
    img.save(io_buffer)
    qr_img_str = base64.b64encode(io_buffer.getvalue()).decode()
    return qr_img_str
