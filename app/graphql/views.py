from flask_graphql import GraphQLView

from .schema import schema


def init_app(app):
    app.add_url_rule(
        "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
    )
