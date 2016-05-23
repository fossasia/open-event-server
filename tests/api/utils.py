

def create_path(*args):
    """Returns API base path with passed arguments appended as path
    parameters.

    '/api/v2/events' + '/arg1/arg2/arg3'

    e.g. create_url(2, 'tracks', 7) -> '/api/v2/events/2/tracks/7'
    """
    url = '/api/v2/events'
    if args:
        url += '/' + '/'.join(map(str, args))
    return url
