from app.models import db


class CustomFormTranslates(db.Model):
    """Custom Form Translates database model"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    custom_form_id = db.Column(
        db.Integer, db.ForeignKey('custom_forms.id', ondelete='CASCADE')
    )
    custom_form = db.relationship(
        'CustomForms', backref='custom_form_translate', foreign_keys=[custom_form_id]
    )
    language_code = db.Column(db.String, nullable=False)
    form_id = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<CustomFormTranslate {self.id}>'

    def convert_to_dict(self):
        """Convert object data to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'language_code': self.language_code,
            'form_id': self.form_id,
        }

    @staticmethod
    def check_custom_form_translate(custom_form_id, translate_id):
        """
        check custom form translate
        :param custom_form_id:
        :param translate_id:
        :return:
        """
        try:
            customFormTranslate = (
                CustomFormTranslates.query.filter_by(custom_form_id=custom_form_id)
                .filter_by(id=translate_id)
                .first()
            )
            return customFormTranslate
        except ModuleNotFoundError:
            return None
