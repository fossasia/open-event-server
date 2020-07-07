from app.models.page import Page
from tests.factories import common
from tests.factories.base import BaseFactory


class PageFactory(BaseFactory):
    class Meta:
        model = Page

    name = common.string_
    title = common.string_
    url = '/new_page'
    description = common.string_
    place = common.string_
    language = 'English'
    index = 0
