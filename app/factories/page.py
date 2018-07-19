import factory

import app.factories.common as common
from app.models.page import db, Page


class PageFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Page
        sqlalchemy_session = db.session

    name = common.string_
    title = common.string_
    url = '/new_page'
    description = common.string_
    place = common.string_
    language = 'English'
    index = 0
