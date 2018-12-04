from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections
from flask_elasticsearch import FlaskElasticsearch

from config import Config

client = FlaskElasticsearch()


def connect_from_config():
    """Create connection for `elasticsearch_dsl`"""
    es_store = Elasticsearch([Config.ELASTICSEARCH_HOST])
    connections.create_connection(hosts=[Config.ELASTICSEARCH_HOST])

    return es_store
