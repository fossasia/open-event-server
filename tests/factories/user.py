from app.models.user import User
from tests.factories import common
from tests.factories.base import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

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
