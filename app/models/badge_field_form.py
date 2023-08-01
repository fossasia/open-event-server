from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY

from app.models import db


class BadgeFieldForms(db.Model):
    """Badge Field Form database model"""

    id = db.Column(db.Integer, primary_key=True)
    badge_form_id = db.Column(
        db.Integer, db.ForeignKey('badge_forms.id', ondelete='CASCADE')
    )
    badge_form = db.relationship(
        'BadgeForms', backref='badge_field_forms_', foreign_keys=[badge_form_id]
    )
    badge_id = db.Column(db.String, nullable=False)
    field_identifier = db.Column(db.String, nullable=True)
    custom_field = db.Column(db.String, nullable=True)
    sample_text = db.Column(db.String, nullable=True)
    font_size = db.Column(db.Integer, nullable=True)
    font_name = db.Column(db.String, nullable=True)
    font_weight = db.Column(ARRAY(db.JSON), nullable=True)
    font_color = db.Column(db.String, nullable=True)
    text_rotation = db.Column(db.Integer, nullable=True)
    text_alignment = db.Column(db.String, nullable=True)
    text_type = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, nullable=True)
    margin_top = db.Column(db.Integer, nullable=True)
    margin_bottom = db.Column(db.Integer, nullable=True)
    margin_left = db.Column(db.Integer, nullable=True)
    margin_right = db.Column(db.Integer, nullable=True)
    qr_custom_field = db.Column(ARRAY(String), nullable=True)
    is_field_expanded = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<BadgeFieldForms {self.id}>'

    def convert_to_dict(self):
        """Convert object data to dictionary"""
        return {
            'id': self.id,
            'field_identifier': self.field_identifier,
            'custom_field': self.custom_field,
            'sample_text': self.sample_text,
            'badge_id': self.badge_id,
            'font_size': self.font_size,
            'font_name': self.font_name,
            'font_weight': self.font_weight,
            'font_color': self.font_color,
            'text_rotation': self.text_rotation,
            'text_alignment': self.text_alignment,
            'text_type': self.text_type,
            'is_deleted': self.is_deleted,
            'margin_top': self.margin_top,
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'margin_right': self.margin_right,
            'qr_custom_field': self.qr_custom_field,
            'is_field_expanded': self.is_field_expanded,
        }

    def get_badge_field(self):
        """Support for only api from ticket #8982"""
        return {
            'id': self.id,
            'field_identifier': self.field_identifier,
            'custom_field': self.custom_field,
        }

    @staticmethod
    def get_badge_field_form_if_exist(badge_field_id, badge_id):
        """
        check custom form translate
        :param badge_field_id:
        :param badge_id:
        :return:
        """
        try:
            badgeFieldForm = (
                BadgeFieldForms.query.filter_by(badge_id=badge_id)
                .filter_by(id=badge_field_id)
                .first()
            )
            return badgeFieldForm
        except ModuleNotFoundError:
            return None
