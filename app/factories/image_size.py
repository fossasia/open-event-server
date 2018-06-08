import factory

import app.factories.common as common
from app.models.image_size import db, ImageSizes


class EventImageSizeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ImageSizes
        sqlalchemy_session = db.session

    type = common.string_
    full_width = 10
    full_height = 10
    full_aspect = True
    full_quality = 10
    icon_width = 10
    icon_height = 10
    icon_aspect = True
    icon_quality = 10
    thumbnail_width = 10
    thumbnail_height = 10
    thumbnail_aspect = True
    thumbnail_quality = 10
    logo_width = 10
    logo_height = 10


class SpeakerImageSizeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ImageSizes
        sqlalchemy_session = db.session

    type = common.string_
    icon-size-quality = 80
    small-size-width-height = 50
    thumbnail-size-quality = None
    icon-size-width-height = 35
    thumbnail-size-width-height = 500
    small-size-quality = 80
