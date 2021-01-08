from app.models import db


def init_app(app):
    @app.shell_context_processor
    def shell_context():
        models = {
            model.__name__: model
            for model in list(db.Model._decl_class_registry.values())
            if getattr(model, '__table__', None) is not None
        }
        return dict(db=db, **models)
