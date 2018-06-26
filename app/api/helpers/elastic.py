"""Elasticsearch helper functions"""


def to_dict(response):
    "Converts elasticsearch responses to dicts for serialization"
    response = response.to_dict()
    response['meta'] = response.meta.to_dict()

    return response
