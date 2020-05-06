def create_app():
    from .instance import current_app

    return current_app
