import factory
from app.models.image_config import db, ImageConfig
import app.factories.common as common


class ImageConfigFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ImageConfig
        sqlalchemy_session = db.session

    page = common.string_
    size = common.string_
