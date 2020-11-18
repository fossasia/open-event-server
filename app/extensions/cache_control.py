from flask import request

counter = 0


def init_app(app):
    @app.after_request
    def add_cache_control(response):
        global counter
        counter += 1
        print('hi', counter)
        if request.method not in ['GET', 'HEAD']:
            return response
        response.headers['X-Response-Counter'] = counter
        if 'Cache-Control' not in response.headers:
            response.cache_control.max_age = 1
            # response.cache_control.private = True
            response.cache_control['stale-while-revalidate'] = 10
        return response
