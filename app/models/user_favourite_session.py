from flask_jwt_extended import current_user

from app.models import db
from app.models.helpers.timestamp import Timestamp


class UserFavouriteSession(db.Model, Timestamp):
    __tablename__ = 'user_favourite_sessions'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='uq_session_user'),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    session = db.relationship('Session', backref='favourites')
    user = db.relationship('User', backref='favourite_sessions')

    @property
    def safe_user(self):
        from app.api.helpers.permission_manager import require_current_user
        from app.models.user import User

        if not self.user_id:
            return None
        can_access = require_current_user() and (
            current_user.is_staff or current_user.id == self.user_id
        )
        if not self.user.is_profile_public and not can_access:
            name = self.user.anonymous_name
            return User(
                id=self.user.id,
                email='example@eventyay.com',
                public_name=name,
            )
        return self.user
