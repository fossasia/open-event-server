import factory
import datetime
# use camelCase for naming variables

string_ = 'example'
email_ = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
integer_ = 25
url_ = 'http://example.com'
imageUrl_ = 'https://www.w3schools.com/html/pic_mountain.jpg'
# date_ = '2016-12-13T23:59:59.123456+00:00'
date_ = datetime.datetime(2016, 12, 13)
# dateFuture_ = '2099-12-13T23:59:59.123456+00:00'
dateFuture_ = datetime.datetime(2099, 12, 13)
# dateEndFuture_ = '2099-12-14T23:59:59.123456+00:00'
dateEndFuture_ = datetime.datetime(2099, 12, 14)
# dateEnd_ = '2020-12-14T23:59:59.123456+00:00'
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
