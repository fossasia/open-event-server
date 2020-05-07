from graphene_sqlalchemy import SQLAlchemyObjectType

from app.models.setting import Setting
from app.api.schema.settings import SettingSchemaPublic
from app.graphql.utils.fields import extract_from_marshmallow


class Settings(SQLAlchemyObjectType):
    class Meta:
        model = Setting
        only_fields = extract_from_marshmallow(SettingSchemaPublic)
