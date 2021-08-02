import graphene

from app.models.setting import Setting

from .types.settings.schema import Settings


class Query(graphene.ObjectType):
    settings = graphene.Field(Settings)

    def resolve_settings(self, info):
        return Setting.query.first()


schema = graphene.Schema(query=Query)
