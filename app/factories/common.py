import factory
import datetime
from app.api.helpers.utilities import static_page, image_link
# use camelCase for naming variables

string_ = 'example'
email_ = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
integer_ = 25
url_ = static_page
imageUrl_ = image_link
date_ = datetime.datetime(2016, 12, 13)
dateFuture_ = datetime.datetime(2099, 12, 13)
dateEndFuture_ = datetime.datetime(2099, 12, 14)
dateEnd_ = datetime.datetime(2020, 12, 14)
country_ = 'US'
currency_ = 'USD'
int_ = '1'
float_ = '1.23456789'
timezone_ = 'UTC'
environment_ = 'production'
secret_ = 'ABCDefghIJKLmnop'
fee_ = '1.23'
slug_ = factory.Sequence(lambda n: 'example_slug{0}'.format(n))


def socialUrl_(name):
    return 'https://{}.com/{}'.format(name, name)
