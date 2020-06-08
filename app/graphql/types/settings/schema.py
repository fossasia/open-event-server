from graphene_sqlalchemy import SQLAlchemyObjectType

from app.api.schema.settings import SettingSchemaPublic
from app.graphql.utils.fields import extract_from_marshmallow
from app.models.setting import Setting


class Settings(SQLAlchemyObjectType):
    class Meta:
        model = Setting
        only_fields = extract_from_marshmallow(SettingSchemaPublic)
