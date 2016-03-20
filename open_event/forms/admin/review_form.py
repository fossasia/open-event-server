from flask_wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email

from open_event.models.review import Review
from ...helpers.helpers import get_session_id


def get_reviews():
    """Returns Event speakers"""
    return Review.query.filter_by(session_id=get_session_id())


class ReviewForm(Form):
    """Review form"""
    RATINGS = [
        (5, 'Loved it'),
        (4, 'Liked it'),
        (3, 'Just OK'),
        (2, 'Not that good'),
        (1, 'Didn\'t like it'),
    ]

    name = StringField('Name', [DataRequired()])
    email = StringField('Email', [DataRequired(), Email()])
    comment = TextAreaField('Comment')
    rating = SelectField('Rating', [DataRequired()], choices=RATINGS, coerce=int)
