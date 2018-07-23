import factory

import app.factories.common as common
from app.models.user import db, User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    email = common.email_
    password = 'password'
    avatar_url = common.imageUrl_
    is_super_admin = False
    is_admin = True
    is_verified = True
    first_name = 'John'
    last_name = 'Doe'
    details = common.string_
    contact = common.string_
    facebook_url = common.socialUrl_('facebook')
    twitter_url = common.socialUrl_('twitter')
    instagram_url = common.socialUrl_('instagram')
    google_plus_url = common.socialUrl_('plus.google')
    thumbnail_image_url = common.imageUrl_
    small_image_url = common.imageUrl_
    icon_image_url = common.imageUrl_
