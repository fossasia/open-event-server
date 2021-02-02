def create_app():
    from .instance import current_app as app

    return app
