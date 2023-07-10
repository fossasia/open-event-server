from app.api.schema.translation_channels import TranslationChannelSchema
from app.api.schema.video_stream import VideoStreamSchema
from app.models.translation_channels import TranslationChannel
from app.models import db
from flask_rest_jsonapi import ResourceList, ResourceRelationship,ResourceDetail




class TranslationChannelsList(ResourceList):
   
    
    def query(self, view_kwargs):
        def print_out(objs):
            print(objs)
            for obj in objs:
                for column in obj.__table__.columns:
                    column_name = column.name
                    column_value = getattr(obj, column_name)
                    print(f"{column_name}: {column_value}")

        """
        Query related channels (transaltions) for specific video stream
        """
        if view_kwargs.get("video_stream_id"):
            print("-----TranslationChannelsList query--------")
            stream_id = view_kwargs.get("video_stream_id")
            print(stream_id)
            
            #Do not use all() as it returns a list of object, needs BaseQuery object
            records = self.session.query(TranslationChannel).filter_by(video_stream_id=stream_id)
            print_out(records)
            return records
            
    schema = TranslationChannelSchema
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {
            "query": query
        },
    }

class TranslationChannelsListPost(ResourceList):
    schema = TranslationChannelSchema
    methods = [
        'POST'
    ]
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {
        }
    } 

class TranslationChannelsDetail(ResourceDetail):
    schema = TranslationChannelSchema
    methods = [
         'GET', 'PATCH', 'DELETE'
    ]
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {
        },
    }
    
class TranslationChannelsRelationship(ResourceRelationship):
    schema = TranslationChannelSchema
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {
        },
    }