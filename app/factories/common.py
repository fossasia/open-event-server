# use camelCase for naming variables

string_ = 'example'
email_ = 'example@example.com'
url_ = 'http://example.com'
imageUrl_ = 'http://example.com/example.png'
date_ = '2016-12-13T23:59:59.123456+00:00'
dateEnd_ = '2016-12-14T23:59:59.123456+00:00'
country_ = 'US'
currency_ = 'USD'
float_ = '1.23456789'
timezone_ = 'UTC'
slug_ = 'camp-trip-retreat'

def socialUrl_(name):
    return 'https://{}.com/{}'.format(name, name)
