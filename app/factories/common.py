# use camelCase for naming variables

string_ = 'example'
email_ = 'example@example.com'
url_ = 'http://example.com'
imageUrl_ = 'http://example.com/example.png'
date_ = '2016-12-13T23:59:59.123456+00:00'


def socialUrl_(name):
    return 'https://{}.com/{}'.format(name, name)
