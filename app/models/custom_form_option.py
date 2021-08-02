from app.models import db
from app.models.base import SoftDeletionModel


class CustomFormOptions(SoftDeletionModel):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False)
    custom_form_id = db.Column(
        db.Integer, db.ForeignKey('custom_forms.id', ondelete='CASCADE')
    )

    def __repr__(self):
        return '<CustomFormOption %r>' % self.id
