import datetime

import factory

from app.api.helpers.utilities import image_link, static_page

# use camelCase for naming variables

string_ = 'example'
email_ = factory.Sequence(lambda n: f'user{n}@example.com')
integer_ = 25
url_ = static_page
imageUrl_ = image_link
date_ = datetime.datetime(2016, 12, 13)
dateFuture_ = datetime.datetime(2099, 12, 13)
dateEndFuture_ = datetime.datetime(2099, 12, 14)
dateEnd_ = datetime.datetime(2030, 12, 14)
country_ = 'US'
currency_ = 'USD'
int_ = '1'
float_ = '1.23456789'
timezone_ = 'UTC'
environment_ = 'testing'
secret_ = 'ABCDefghIJKLmnop'
fee_ = 1.23
average_rating_ = 3
rating_count_ = 1
slug_ = factory.Sequence(lambda n: f'example_slug{n}')


def socialUrl_(name):
    return f'https://{name}.com/{name}'
