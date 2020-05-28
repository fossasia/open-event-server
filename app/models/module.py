from app.models import db


class Module(db.Model):
    """File model class"""

    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    ticket_include = db.Column(db.Boolean, default=False)
    payment_include = db.Column(db.Boolean, default=False)
    donation_include = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Module %r>' % self.id
