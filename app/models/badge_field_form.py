from app.models import db


class BadgeFieldForms(db.Model):
    """Badge Field Form database model"""

    id = db.Column(db.Integer, primary_key=True)
    badge_form_id = db.Column(
        db.Integer, db.ForeignKey('badge_forms.id', ondelete='CASCADE')
    )
    badge_form = db.relationship(
        'BadgeForms', backref='badge_field_form', foreign_keys=[badge_form_id]
    )
    badge_id = db.Column(db.String, nullable=False)
    custom_field = db.Column(db.String, nullable=False)
    sample_text = db.Column(db.String, nullable=False)
    font_size = db.Column(db.Integer, nullable=False)
    font_name = db.Column(db.String, nullable=False)
    font_weight = db.Column(db.String, nullable=False)
    font_color = db.Column(db.String, nullable=False)
    text_rotation = db.Column(db.Integer, nullable=False)
    text_alignment = db.Column(db.String, nullable=False)
    text_type = db.Column(db.String, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)
    margin_top = db.Column(db.Integer, nullable=False)
    margin_bottom = db.Column(db.Integer, nullable=False)
    margin_left = db.Column(db.Integer, nullable=False)
    margin_right = db.Column(db.Integer, nullable=False)
    qr_custom_field = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<BadgeFieldForm {self.id}>'

    def convert_to_dict(self):
        """Convert object data to dictionary"""
        return {
            'id': self.id,
            'custom_field': self.custom_field,
            'sample_text': self.sample_text,
            'badge_id': self.badge_id,
            'font_size': self.font_size,
            'text_alignment': self.text_alignment,
            'text_type': self.text_type,
            'is_deleted': self.is_deleted,
        }

    @staticmethod
    def check_badge_field_form(badge_form_id, badge_field_form_id):
        """
        check custom form translate
        :param badge_form_id:
        :param badge_field_form_id:
        :return:
        """
        try:
            badgeFieldForm = (
                BadgeFieldForms.query.filter_by(badge_form_id=badge_form_id)
                .filter_by(id=badge_field_form_id)
                .first()
            )
            return badgeFieldForm
        except ModuleNotFoundError:
            return None
