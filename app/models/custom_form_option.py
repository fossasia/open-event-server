from app.models import db
from app.models.base import SoftDeletionModel


class CustomFormOptions(SoftDeletionModel):
    __tablename__ = 'custom_form_options'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False)
    custom_form_id = db.Column(db.Integer, db.ForeignKey('custom_forms.id', ondelete='CASCADE'))

    def __init__(self,
                 custom_form_id=None,
                 deleted_at=None,
                 value=None):
        self.custom_form_id = custom_form_id
        self.value = value
        self.deleted_at = deleted_at

    def __repr__(self):
        return '<CustomFormOption %r>' % self.id

    def __str__(self):
        return self.__repr__()
